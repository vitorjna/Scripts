# POS Translate

This script (`pos_translate.py`) is a Python-based tool designed to translate English text into multiple languages specifically for Point of Sale (POS) terminals and payment screen prompts using Google's Gemini API.

## Features

*   **Multi-Language Translation**: Translates English text into 25 target languages in a single API call using ISO 639-1 language codes.
*   **Concise POS-Oriented Output**: Translations are tailored for Point of Sale (POS) terminal displays, emphasizing concise phrasing and standard payment/card-handling terminology.
*   **Gemini API Integration**: Leverages the Gemini API for fast and context-aware translations.
*   **Zero External Dependencies**: Built entirely with Python standard libraries (`urllib`, `json`, `os`).
*   **Configurable API Key**: Loads the Gemini API key securely from a local `.env` file.
*   **Model Listing**: Lists available models from the Gemini API directly from the console.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/POSTranslate
    ```

2.  **Environment Variables**: Before running the script, configure your Gemini API token. Copy the template `.env.example` to `.env` and set your `GEMINI_API_TOKEN`:

    ```bash
    cp .env.example .env
    # Edit .env and add your GEMINI_API_TOKEN
    ```

3.  **Dependencies**: Ensure Python 3 is installed. No third-party packages are required.

4.  **Running the Script**: Execute the translator from the `POSTranslate` directory:

    ```bash
    python pos_translate.py
    ```

    - Enter the English text you want translated for POS screens.
    - Type `listmodels` to view available Gemini models.
    - The formatted translations for all target languages will be printed to the console.