# Subtitle Translator

Python scripts to translate `.srt` subtitle files:
- **`translate_subs_llm.py`**: Context-aware translation using Local (LM Studio, Ollama) or Cloud (Gemini, OpenAI) LLMs.
- **`translate_subs.py`**: Fast, multi-threaded translation via Google Translate web API.

---

## Features (LLM Version)

- **Context-Aware**: Uses surrounding subtitle blocks and prior translations to preserve scene context and tone.
- **Sync Protection**: Validates response line counts to prevent subtitle desync; strips `<think>`/`<thought>` reasoning tags.
- **Crash Recovery**: Resumes interrupted files from the last translated block.
- **Smart Naming**: Auto-strips `.eng` and preserves `.sdh` tags (e.g., `movie.eng.sdh.srt` $\rightarrow$ `movie.pt.sdh.srt`).
- **Watch Mode**: Monitors a folder, translates new `.srt` files, and moves originals to `processed/`.
- **Per-file Logs**: Writes logs alongside subtitles (`<filename>_<lang>.log`).

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `config.json`:**
   Copy `config.example.json` to `config.json`:
   ```json
   {
     "llm_provider": "local",
     "local": {
       "base_url": "http://127.0.0.1:1234/v1/",
       "model_name": "gemma-4-e4b-it"
     },
     "cloud": {
       "api_key": "YOUR_API_KEY",
       "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
       "model_name": "gemma-4-26b-a4b-it"
     },
     "translation": {
       "target_language": "pt-PT",
       "output_suffix": ".pt",
       "context_blocks_previous": 5,
       "context_blocks_next": 3
     },
     "watch_folder": "./subs"
   }
   ```

---

## Usage

### LLM Translator
```bash
# Single file
python translate_subs_llm.py path/to/subtitle.srt

# Override language
python translate_subs_llm.py path/to/subtitle.srt --target-lang "es"

# Watch mode (monitors watch_folder from config.json)
python translate_subs_llm.py
```

### Google Translator
```bash
# Fast multi-threaded translation
python translate_subs.py path/to/subtitle.srt --target-lang "pt-PT"
```

---

## Comparison

| Feature | LLM (`translate_subs_llm.py`) | Google (`translate_subs.py`) |
| :--- | :---: | :---: |
| **Context & Nuance** | Yes (sliding window) | No |
| **Resume Interrupted** | Yes | No |
| **Watch Folder** | Yes (`processed/` archive) | No |
| **Speed / Concurrency** | Sequential | Multi-threaded (30 workers) |
| **Requirements** | Local LLM / Cloud API key | None |
| **Best For** | Movies & TV shows | Fast bulk translations |
