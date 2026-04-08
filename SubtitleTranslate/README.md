# Subtitle Translator

This collection contains Python-based scripts to automate the translation of `.srt` subtitle files. It includes a fast, multi-threaded Google Translate version and a more sophisticated LLM-powered version that uses context from surrounding subtitle blocks for higher quality results.

## Scripts

### 1. LLM Translator (`translate_subs_llm.py`)
This is the advanced version that leverages Large Language Models (LLMs) to provide context-aware translations.

*   **Contextual Awareness**: Sends preceding and following subtitle blocks as context to the LLM to ensure consistent terminology and better flow.
*   **Provider Support**: Works with any OpenAI-compatible API (e.g., Local LLMs via LM Studio/Ollama, or Cloud APIs like Google AI Studio / Gemini).
*   **Watch Mode**: Can monitor a specific folder for new `.srt` files and translate them automatically as they arrive.
*   **Resume Capability**: If interrupted, it can resume from the last translated block by checking the existing output file.
*   **Robustness**: Includes automatic retries and validation to ensure the translated text has the same number of lines as the original.

### 2. Google Translator (`translate_subs.py`)
A lightweight and fast translator using the Google Translate web API.

*   **High Speed**: Uses multi-threading (`ThreadPoolExecutor`) to translate multiple subtitle blocks simultaneously.
*   **No API Key Required**: Uses the public Google Translate interface.
*   **Simple Usage**: Ideal for quick translations where contextual nuance is less critical.

---

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Mainly requires `openai` for the LLM script)*

2.  **Configuration**:
    - Rename `config.example.json` to `config.json`.
    - Edit `config.json` with your preferred settings:
        - `llm_provider`: "cloud" or "local".
        - `cloud`/`local`: API keys, base URLs, and model names.
        - `translation`: Set your `target_language` and `output_suffix`.
        - `watch_folder`: The directory to monitor in watch mode.

---

## Usage

### Using the LLM Translator
**Single File:**
```bash
python translate_subs_llm.py path/to/your/subtitle.srt
```

**Watch Mode (Auto-process folder):**
Make sure `watch_folder` is set in `config.json`, then run:
```bash
python translate_subs_llm.py
```


### Using the Google Translator
```bash
python translate_subs.py path/to/your/subtitle.srt --target-lang "pt-PT"
```

## Features Summary
| Feature | LLM version | Google version |
| :--- | :---: | :---: |
| Context-Aware | Yes | No |
| Multi-threaded | No | Yes |
| Watch Folder | Yes | No |
| API Key Needed | Yes (Cloud) / No (Local) | No |
| Best for | Quality & Accuracy | Speed |
