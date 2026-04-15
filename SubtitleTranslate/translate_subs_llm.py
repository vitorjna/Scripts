import os
import json
import time
import logging
import argparse
import shutil
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# _USER_PROMPT_TEMPLATE = """Translate the subtitle block below from English to {target_lang}.
# STRICT RULES:
# - Your response must contain ONLY the translated lines of the 'lines_to_translate' array inside the JSON data.
# - Consider the context provided in 'previous_context' and 'following_context' to make a better translation.
# - Do NOT output anything from the context sections, nor any JSON structure.
# - Do NOT add any preamble, explanation, labels, or quotes.
# - Handle special cases: if the original text contains misspellings, plays on words, slang, or other linguistic nuances, reflect a similar misspelling, equivalent wordplay, or corresponding style in the translation.
# - Pay attention to gendered words and try to guess and match the gender of the character saying each line. If possible, and if it doesn't affect the meaning, remove gendered words when there's too much ambiguity.

# EXPECTED LINE COUNT: {expected_line_count}

# {json_payload}"""

_USER_PROMPT_TEMPLATE = """You are an expert audiovisual translator specializing in movie and television subtitles. Your task is to translate the specified subtitle lines from English into {target_lang}.
### STRICT INSTRUCTIONS:

1. FORMATTING & OUTPUT:
- Output ONLY the translated plain text of the `lines_to_translate` array.
- DO NOT output JSON syntax, lists, quotes, labels, or conversational filler (e.g., "Here is the translation:").
- PRESERVE EXACT LINES: Your response MUST contain the exact same number of lines and line breaks as the original `lines_to_translate` array. Do not merge or split subtitle lines.

2. CONTEXT USAGE:
- Read `previous_context` and `following_context` purely to understand the scene, tone, and continuity.
- DO NOT translate or include any text from the context sections in your final output.

3. LOCALIZATION & TONE:
- Adapt slang, idioms, puns, and intentional misspellings into natural equivalents in {target_lang}.
- Maintain the original tone, register, and character voice.

4. GENDER & GRAMMAR:
- Use the context to infer the correct grammatical gender for the speaker and the person being spoken to.
- If the gender is ambiguous and cannot be guessed from the context, use gender-neutral phrasing in {target_lang} whenever possible, provided it sounds natural.

### INPUT DATA:
{json_payload}"""


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
    """Remove any empty lines or prompt delimiter lines the LLM may have echoed back."""
    lines = translated.splitlines()
    # Filter out empty lines
    cleaned = [line for line in lines if line.strip()]
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

    lines_to_translate = [l for l in text.splitlines() if l.strip()]
    expected_line_count = len(lines_to_translate)

    json_payload_data = {
        "previous_context": [l for l in prev_text.splitlines() if l.strip()] if prev_text else [],
        "lines_to_translate": lines_to_translate,
        "following_context": [l for l in next_text.splitlines() if l.strip()] if next_text else []
    }
    json_payload = json.dumps(json_payload_data, indent=0, ensure_ascii=False)

    user_prompt = _USER_PROMPT_TEMPLATE.format(
        target_lang=target_lang,
        expected_line_count=expected_line_count,
        json_payload=json_payload
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
                "max_tokens": 2048,
                "temperature": 0.1,
                "top_p": 0.95
            }
            if extra_body is not None:
                kwargs["extra_body"] = extra_body

            # logging.info(f"Messages: {messages}")

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


def translate_file(srt_path: str, target_lang: str, output_suffix: str) -> bool:
    if not os.path.exists(srt_path):
        logging.error(f"File not found: {srt_path}")
        return False

    # Setup file logging for this specific subtitle file
    log_filename = f"log_{os.path.basename(srt_path)}"
    log_path = os.path.join(os.path.dirname(os.path.abspath(srt_path)), log_filename)
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)

    try:
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

        parsed_blocks = []
        for b in blocks:
            lines = b.split('\n')
            if len(lines) >= 3:
                parsed_blocks.append({
                    "block_num": lines[0].strip(),
                    "timestamp": lines[1].strip(),
                    "original_text": "\n".join(lines[2:]).strip(),
                    "translated_text": None,
                    "raw": b
                })
            else:
                parsed_blocks.append({
                    "block_num": "",
                    "timestamp": "",
                    "original_text": "",
                    "translated_text": None,
                    "raw": b
                })

        # Construct output filename: [name].[target_lang][.sdh].srt
        # Logic: remove .eng, keep .sdh but place it after target_lang (output_suffix)
        dirname = os.path.dirname(srt_path)
        basename = os.path.basename(srt_path)
        if basename.lower().endswith(".srt"):
            basename = basename[:-4]

        parts = basename.split('.')
        new_parts = []
        is_sdh = False
        for p in parts:
            if p.lower() == 'eng':
                continue
            if p.lower() == 'sdh':
                is_sdh = True
                continue
            new_parts.append(p)

        # Add the language identifier (strip leading dot from suffix if present)
        new_parts.append(output_suffix.lstrip('.'))

        if is_sdh:
            new_parts.append('sdh')

        output_filename = ".".join(new_parts) + ".srt"
        output_path = os.path.join(dirname, output_filename)
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
                start_index = min(start_index, len(parsed_blocks))
                logging.info(f"Found {start_index} already translated blocks. Resuming from block {start_index + 1}.")

                # Populate previously translated texts into the parsed container
                for i in range(start_index):
                    lines = already_translated_list[i].split('\n')
                    if len(lines) >= 3:
                        parsed_blocks[i]["translated_text"] = "\n".join(lines[2:]).strip()
                    else:
                        parsed_blocks[i]["translated_text"] = parsed_blocks[i]["original_text"]
        else:
            logging.info(f"No existing output file found at {output_path}.")

        if start_index >= len(parsed_blocks):
            logging.info(f"All blocks in {srt_path} are already translated.")
            return True

        logging.info(f"Preparing blocks to process (starting from index {start_index})...")
        mode = 'a' if start_index > 0 else 'w'
        logging.info(f"Opening output file in mode '{mode}'...")

        try:
            with open(output_path, mode, encoding='utf-8', newline='') as f:
                logging.info("Output file opened successfully.")
                for actual_index in range(start_index, len(parsed_blocks)):
                    block_data = parsed_blocks[actual_index]

                    if not block_data["original_text"]:
                        f.write(block_data["raw"] + "\n\n")
                        f.flush()
                        continue

                    context_prev_count = CONFIG.get("translation", {}).get("context_blocks_previous", 2)
                    context_next_count = CONFIG.get("translation", {}).get("context_blocks_next", 2)

                    # Get preceding texts (translated text preferred for consistency)
                    prev_texts = []
                    for i in range(max(0, actual_index - context_prev_count), actual_index):
                        txt = (parsed_blocks[i].get("translated_text") or parsed_blocks[i].get("original_text") or "").strip()
                        if txt:
                            prev_texts.append(txt)
                    prev_text = "\n\n".join(prev_texts)

                    # Get following texts (original texts)
                    next_texts = []
                    for i in range(actual_index + 1, min(len(parsed_blocks), actual_index + 1 + context_next_count)):
                        txt = (parsed_blocks[i].get("original_text") or "").strip()
                        if txt:
                            next_texts.append(txt)
                    next_text = "\n\n".join(next_texts)

                    logging.info(f"Translating block {actual_index + 1}/{len(parsed_blocks)}...")
                    translated_text = translate_llm(block_data["original_text"], target_lang, prev_text, next_text)

                    # Store back translated text to be used as context for future blocks
                    parsed_blocks[actual_index]["translated_text"] = translated_text

                    result = f"{block_data['block_num']}\n{block_data['timestamp']}\n{translated_text}"
                    f.write(result + "\n\n")
                    f.flush()
                    logging.info(f"Processed block {actual_index + 1}/{len(parsed_blocks)}")

            logging.info(f"Translation complete! Saved to {output_path}")
            return True

        except KeyboardInterrupt:
            logging.info("\nTranslation interrupted by user.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred during processing: {e}")
            return False
    finally:
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()


def watch_directory(folder: str, target_lang: str, output_suffix: str):
    if not os.path.exists(folder) or not os.path.isdir(folder):
        logging.error(f"Watch directory does not exist or is not a folder: {folder}")
        return

    processed_folder = os.path.join(folder, "processed")
    os.makedirs(processed_folder, exist_ok=True)

    logging.info(f"Watching folder '{folder}' for new .srt files (skipping files with '{output_suffix}')...")
    logging.info(f"Successfully processed files will be moved to '{processed_folder}'.")
    logging.info("Press Ctrl+C to stop.")

    processed_files = {}  # Map path -> mtime
    try:
        while True:
            for filename in os.listdir(folder):
                srt_path = os.path.join(folder, filename)
                if not os.path.isfile(srt_path):
                    continue

                # Filter logic: skip logs, non-srt files, and files that already contain the output suffix.
                is_srt = filename.lower().endswith(".srt")
                is_log = filename.lower().startswith("log_")
                clean_suffix = output_suffix.lower().lstrip('.')
                # A file is considered already processed if it contains ".suffix." or ends with ".suffix.srt"
                already_labeled = f".{clean_suffix}." in filename.lower() or filename.lower().endswith(f".{clean_suffix}.srt")

                if is_srt and not is_log and not already_labeled:
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
