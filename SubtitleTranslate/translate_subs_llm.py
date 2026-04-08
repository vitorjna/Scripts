import os
import json
import time
import logging
import argparse
import shutil
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prompt block constants
_SECTION_PREV_CONTEXT = "--- CONTEXT (preceding, do NOT translate) ---"
_SECTION_NEXT_CONTEXT = "--- CONTEXT (following, do NOT translate) ---"
_SECTION_END_CONTEXT = "--- END CONTEXT ---"
_SECTION_TEXT = "--- TEXT TO TRANSLATE ---"
_SECTION_END_TEXT = "--- END TEXT ---"
_SECTION_TRANSLATION = "TRANSLATION (translated lines only):"

_CONTEXT_MARKERS = [
    _SECTION_PREV_CONTEXT,
    _SECTION_NEXT_CONTEXT,
    _SECTION_END_CONTEXT,
    _SECTION_TEXT,
    _SECTION_END_TEXT,
    _SECTION_TRANSLATION,
]

_USER_PROMPT_TEMPLATE = f"""Translate the subtitle block below from English to {{target_lang}}.
STRICT RULES:
- Your response must contain ONLY the translated lines of the '{_SECTION_TEXT.replace('-', '').strip()}' block.
- Consider the context of the original text to provide a better translation.
- Do NOT output anything from the 'CONTEXT' sections.
- Do NOT add any preamble, explanation, labels, or quotes.
- Preserve the exact number of line breaks present in the original text.
- The original text has {{expected_line_count}} line(s); your translation must also have exactly {{expected_line_count}} line(s).

{{prev_section}}{_SECTION_TEXT}
{{text}}
{_SECTION_END_TEXT}

{{next_section}}{_SECTION_TRANSLATION}"""

_PREV_CONTEXT_TEMPLATE = f"{_SECTION_PREV_CONTEXT}\n{{content}}\n{_SECTION_END_CONTEXT}\n\n"
_NEXT_CONTEXT_TEMPLATE = f"{_SECTION_NEXT_CONTEXT}\n{{content}}\n{_SECTION_END_CONTEXT}\n\n"

def load_config():
    """Load configuration from config.json, falling back to config.example.json if not present."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    example_path = os.path.join(os.path.dirname(__file__), 'config.example.json')

    if not os.path.exists(config_path):
        logging.warning(f"Configuration file {config_path} not found. Loading from {example_path}.")
        if not os.path.exists(example_path):
            raise FileNotFoundError(f"Configuration file {example_path} NOT found. Please provide a config file.")
        path_to_load = example_path
    else:
        path_to_load = config_path

    with open(path_to_load, 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize configuration
try:
    CONFIG = load_config()
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    exit(1)


def _strip_context_leakage(translated: str) -> str:
    """Remove any prompt delimiter lines the LLM may have echoed back."""
    lines = translated.splitlines()
    cleaned = [line for line in lines if line.strip() not in _CONTEXT_MARKERS]
    return "\n".join(cleaned).strip()


def _get_client():
    """Initialize and return the OpenAI client based on configuration."""
    provider = CONFIG.get("llm_provider", "cloud")
    if provider == "local":
        local_cfg = CONFIG.get("local", {})
        return OpenAI(
            api_key=local_cfg.get("api_key", ""),
            base_url=local_cfg.get("base_url", "http://localhost:1234/v1"),
            timeout=30.0  # Add a 30s timeout to prevent indefinite blocking
        ), local_cfg.get("model_name"), "local"
    else:
        cloud_cfg = CONFIG.get("cloud", {})
        return OpenAI(
            api_key=cloud_cfg.get("api_key"),
            base_url=cloud_cfg.get("base_url", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            timeout=60.0  # Cloud calls might take longer but still need a timeout
        ), cloud_cfg.get("model_name", "gemma-4-26b-a4b-it"), "cloud"


# Shared client to avoid repeated initializations
try:
    _CLIENT, _MODEL_NAME, _PROVIDER = _get_client()
except Exception as e:
    logging.error(f"Failed to initialize LLM client: {e}")
    exit(1)


def translate_llm(text: str, target_lang: str, prev_text: str = "", next_text: str = "") -> str:
    """Call the configured LLM to translate *text*.

    Retries up to 3 times. On each attempt, validates that the returned
    translation has the same number of lines as the source text. If the
    line counts differ, the attempt is discarded and the call is retried.

    Returns the original *text* unchanged (with a warning) only if all
    retry attempts are exhausted.
    """
    if not text.strip():
        return ""

    system_instr = CONFIG.get("translation", {}).get("system_instruction", "You are a professional subtitle translator.")

    expected_line_count = len(text.splitlines())

    prev_section = _PREV_CONTEXT_TEMPLATE.format(content=prev_text) if prev_text else ""
    next_section = _NEXT_CONTEXT_TEMPLATE.format(content=next_text) if next_text else ""

    user_prompt = _USER_PROMPT_TEMPLATE.format(
        target_lang=target_lang,
        expected_line_count=expected_line_count,
        prev_section=prev_section,
        text=text,
        next_section=next_section
    )

    if "gemma" in _MODEL_NAME.lower() or _PROVIDER != "local":
        # Gemma models generally do not support the 'system' role;
        # merge the system instruction directly into the user message.
        messages = [
            {"role": "user", "content": f"{system_instr}\n\nUSER REQUEST:\n{user_prompt}"}
        ]
    else:
        messages = [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": user_prompt}
        ]

    # Disable chain-of-thought / thinking to keep responses clean for Google cloud API.
    extra_body = None
    if _PROVIDER != "local":
        extra_body = {
            "google": {
                "thinking_config": {
                    "thinking_level": "minimal",
                    "include_thoughts": False
                }
            }
        }

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            kwargs = {
                "model": _MODEL_NAME,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1024,
                "top_p": 0.9,
            }
            if extra_body is not None:
                kwargs["extra_body"] = extra_body

            response = _CLIENT.chat.completions.create(**kwargs)

            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                logging.warning(
                    f"[Block translation] Attempt {attempt}/{max_attempts}: LLM returned an empty response. Retrying..."
                )
                time.sleep(2)
                continue

            translated = _strip_context_leakage(raw.strip())

            if not translated:
                logging.warning(
                    f"[Block translation] Attempt {attempt}/{max_attempts}: Translation was empty after stripping context markers. Retrying..."
                )
                time.sleep(2)
                continue

            actual_line_count = len(translated.splitlines())
            if actual_line_count != expected_line_count:
                logging.warning(
                    f"[Block translation] Attempt {attempt}/{max_attempts}: Line count mismatch — "
                    f"expected {expected_line_count}, got {actual_line_count}. Retrying...\n"
                    f"  Original : {repr(text)}\n"
                    f"  Translated: {repr(translated)}"
                )
                time.sleep(2)
                continue

            return translated

        except Exception as e:
            logging.error(f"[Block translation] Attempt {attempt}/{max_attempts}: Error calling {_PROVIDER} LLM: {e}. Retrying...")
            time.sleep(2)

    logging.warning(
        f"[Block translation] All {max_attempts} attempts failed. Keeping original text:\n  {repr(text)}"
    )
    return text


def extract_text(block_str: str) -> str:
    if not block_str:
        return ""
    texts = []
    for b in block_str.split('\n\n'):
        lines = b.split('\n')
        if len(lines) >= 3:
            texts.append("\n".join([line for i, line in enumerate(lines) if i >= 2]).strip())
    return "\n\n".join(texts).strip()


def process_block(block: str, target_lang: str, prev_block: str = "", next_block: str = "") -> str:
    lines = block.split('\n')
    if len(lines) >= 3:
        block_num = lines[0].strip()
        timestamp = lines[1].strip()
        text_lines = "\n".join(lines[2:]).strip()

        if not text_lines:
            # Empty text body — nothing to translate
            return block

        prev_text = extract_text(prev_block)
        next_text = extract_text(next_block)

        translated_text = translate_llm(text_lines, target_lang, prev_text, next_text)
        return f"{block_num}\n{timestamp}\n{translated_text}"
    else:
        return block


def translate_file(srt_path: str, target_lang: str, output_suffix: str) -> bool:
    if not os.path.exists(srt_path):
        logging.error(f"File not found: {srt_path}")
        return False

    logging.info(f"Reading subtitle file: {srt_path}")
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        logging.warning(f"UTF-8 decoding failed for {srt_path}. Retrying with latin-1...")
        with open(srt_path, 'r', encoding='latin-1') as f:
            text = f.read()

    # Normalise line endings and strip a UTF-8 BOM if present
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')

    blocks = text.strip().split('\n\n')
    # Filter out any completely blank/whitespace-only blocks that can appear in malformed SRTs
    blocks = [b for b in blocks if b.strip()]
    logging.info(f"Total blocks found: {len(blocks)}")

    output_path = srt_path.replace(".srt", f"{output_suffix}.srt")
    start_index: int = 0

    if os.path.exists(output_path):
        logging.info(f"Checking for existing translations in {output_path}...")
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_content = f.read().strip()
        except Exception as e:
            logging.warning(f"Failed to read existing content: {e}")
            existing_content = ""

        if existing_content and len(existing_content) > 5:
            already_translated_list = [b for b in existing_content.split('\n\n') if b.strip()]
            start_index = len(already_translated_list)
            # Ensure we don't start out of bounds bounds if output has more blocks for some reason
            start_index = min(start_index, len(blocks))
            logging.info(f"Found {start_index} already translated blocks. Resuming from block {start_index + 1}.")
    else:
        logging.info(f"No existing output file found at {output_path}.")

    if start_index >= len(blocks):
        logging.info(f"All blocks in {srt_path} are already translated.")
        return True

    logging.info(f"Preparing blocks to process (starting from index {start_index})...")
    blocks_to_process = [b for i, b in enumerate(blocks) if i >= start_index]
    mode = 'a' if start_index > 0 else 'w'
    logging.info(f"Opening output file in mode '{mode}'...")

    try:
        with open(output_path, mode, encoding='utf-8', newline='') as f:
            logging.info("Output file opened successfully.")
            if blocks_to_process:
                for actual_index, block in enumerate(blocks_to_process, start=start_index):
                    # Get 2 preceding and 2 following blocks for context
                    prev_block = "\n\n".join(blocks[max(0, actual_index - 2):actual_index]) if actual_index > 0 else ""
                    next_block = "\n\n".join(blocks[actual_index + 1:actual_index + 3]) if actual_index < len(blocks) - 1 else ""

                    logging.info(f"Translating block {actual_index + 1}/{len(blocks)}...")
                    result = process_block(block, target_lang, prev_block, next_block)
                    f.write(result + "\n\n")
                    f.flush()
                    logging.info(f"Processed block {actual_index + 1}/{len(blocks)}")

        logging.info(f"Translation complete! Saved to {output_path}")
        return True

    except KeyboardInterrupt:
        logging.info("\nTranslation interrupted by user.")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during processing: {e}")
        return False


def watch_directory(folder: str, target_lang: str, output_suffix: str):
    if not os.path.exists(folder) or not os.path.isdir(folder):
        logging.error(f"Watch directory does not exist or is not a folder: {folder}")
        return

    processed_folder = os.path.join(folder, "processed")
    os.makedirs(processed_folder, exist_ok=True)

    logging.info(f"Watching folder '{folder}' for new .srt files (excluding '*{output_suffix}.srt')...")
    logging.info(f"Successfully processed files will be moved to '{processed_folder}'.")
    logging.info("Press Ctrl+C to stop.")

    processed_files = {}  # Map path -> mtime
    try:
        while True:
            for filename in os.listdir(folder):
                srt_path = os.path.join(folder, filename)
                if not os.path.isfile(srt_path):
                    continue

                if filename.lower().endswith(".srt") and not filename.lower().endswith(f"{output_suffix.lower()}.srt"):
                    try:
                        mtime = os.path.getmtime(srt_path)
                    except OSError:
                        continue  # File might have been removed

                    if processed_files.get(srt_path) == mtime:
                        continue  # Already fully translated this version

                    # Found a file that is new or modified
                    logging.info(f"\n--- Processing new or modified file: {filename} ---")
                    try:
                        success = translate_file(srt_path, target_lang, output_suffix)
                        if success:
                            processed_files[srt_path] = mtime
                            dest_path = os.path.join(processed_folder, filename)
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
                            shutil.move(srt_path, dest_path)
                            logging.info(f"Moved '{filename}' to processed folder.")
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        logging.error(f"Failed to process {srt_path}: {e}")

            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("\nStopped watching folder.")


def main():
    parser = argparse.ArgumentParser(description="Translate SRT subtitles using an LLM (local or cloud).")
    parser.add_argument("srt_file", nargs='?', help="Path to the .srt file to translate. If omitted, watches folder defined in config.")
    parser.add_argument("--target-lang", help="Target language (overrides config).")
    args = parser.parse_args()

    # Determine target language and exit if not found
    target_lang = args.target_lang or CONFIG.get("translation", {}).get("target_language")
    if not target_lang:
        logging.error("Target language NOT defined. Please specify 'target_language' in 'config.json' or use '--target-lang'.")
        exit(1)

    output_suffix = CONFIG.get("translation", {}).get("output_suffix", "_llm_translated")

    if args.srt_file:
        try:
            translate_file(args.srt_file, target_lang, output_suffix)
        except KeyboardInterrupt:
            logging.info("\nClosing and exiting...")
    else:
        watch_folder = CONFIG.get("watch_folder")
        if not watch_folder:
            logging.error("No input file provided and 'watch_folder' is not set in config.json.")
            exit(1)
        watch_directory(watch_folder, target_lang, output_suffix)

if __name__ == "__main__":
    main()
