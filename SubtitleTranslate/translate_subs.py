import os
import json
import logging
import argparse
import concurrent.futures
import time
import urllib.request
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """Load configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.exists(config_path):
        logging.warning(f"Configuration file {config_path} not found.")
        return {}
    else:
        path_to_load = config_path

    try:
        with open(path_to_load, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

# Initialize configuration
CONFIG = load_config()

def translate_google(text, target_lang='pt-PT'):
    """Translate text using the Google Translate direct URL."""
    if not text.strip():
        return ""

    # Ensure we use a direct language code if possible
    # (Simple mapping for this specific script's context)
    lang_code = "pt-PT" if "pt-PT" in target_lang.lower() else "pt"
    if "en" in target_lang.lower(): lang_code = "en" # Fallback/debug

    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={lang_code}&dt=t&q=' + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode('utf-8'))
                # Google Translate returns a list of parts; join the first element of each part
                return ''.join([x[0] for x in res[0]])
        except Exception as e:
            logging.warning(f"Google Translate error (attempt {attempt + 1}/3): {e}")
            time.sleep(1) # Retry backoff
            continue

    return text

def process_block(b, target_lang):
    """Parses an SRT block, translates it, and returns the formatted block."""
    lines = b.split('\n')
    if len(lines) >= 3:
        try:
            block_num = lines[0].strip()
            timestamp = lines[1].strip()
            text_lines = "\n".join(lines[2:]).strip()

            if not text_lines:
                return b

            # Translate the subtitle textual part
            translated_text = translate_google(text_lines, target_lang)
            return f"{block_num}\n{timestamp}\n{translated_text}"
        except Exception as e:
            logging.error(f"Error processing block: {e}")
            return b
    else:
        # Return malformed blocks as-is
        return b

def translate_file(srt_path, target_lang, output_suffix):
    if not os.path.exists(srt_path):
        logging.error(f"Input file not found: {srt_path}")
        return

    logging.info(f"Processing subtitle file: {srt_path}")
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        logging.warning(f"UTF-8 decoding failed for {srt_path}. Retrying with latin-1...")
        with open(srt_path, 'r', encoding='latin-1') as f:
            text = f.read()

    # Normalise line endings and strip UTF-8 BOM
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    blocks = text.strip().split('\n\n')
    logging.info(f"Total blocks found: {len(blocks)}")

    results = [None] * len(blocks)

    # Utilize ThreadPoolExecutor to translate blocks in multithreading mode efficiently
    # Google Translate has stricter rate limits than some APIs, but 20-30 threads usually works okay for small files.
    max_workers = 30

    logging.info(f"Translating with {max_workers} threads...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_block, b, target_lang): i for i, b in enumerate(blocks)}
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            results[i] = future.result()

    output_path = srt_path.replace(".srt", f"{output_suffix}.srt")

    # Write reconstructed blocks into output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(results) + "\n")
        logging.info(f"Translation complete! Saved to {output_path}")
    except Exception as e:
        logging.error(f"Error writing output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Translate SRT subtitles using Google Translate.")
    parser.add_argument("srt_file", help="Path to the .srt file to translate.")
    parser.add_argument("--target-lang", help="Target language code (e.g. pt-PT).")
    parser.add_argument("--suffix", help="Output file suffix.")

    args = parser.parse_args()

    # Determine target language and suffix from config or arguments
    target_lang = args.target_lang or CONFIG.get("translation", {}).get("target_language", "pt-PT")
    output_suffix = args.suffix or CONFIG.get("translation", {}).get("output_suffix", "_translated")

    try:
        translate_file(args.srt_file, target_lang, output_suffix)
    except KeyboardInterrupt:
        logging.info("\nInterrupted by user. Exiting...")

if __name__ == "__main__":
    main()
