# AI Translation

This script (`translate.py`) is a Python-based tool for automated text translation, leveraging external APIs.

## Features

*   **Multi-Language Translation**: Translates English text into a predefined set of target languages.
*   **Concise POS-Oriented Output**: Translations are optimized for Point of Sale (POS) terminal screens, using concise and common terminology for payments and card handling.
*   **Gemini API Integration**: Leverages the Gemini API for robust and accurate translations.
*   **Configurable API Key**: API key is loaded from a `.env` file for secure and flexible configuration.
*   **Model Listing**: Allows users to list available Gemini models directly from the script.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/AI-Translate
    ```

2.  **Environment Variables**: Before running the script, you need to set up your environment variables. A template is provided in `.env.example`. Copy this file to `.env` and fill in the necessary API keys and configurations.

    ```bash
    cp .env.example .env
    # Open .env and add your API keys
    ```

3.  **Dependencies**: Ensure you have Python installed. This script uses standard Python libraries (`json`, `urllib.error`, `urllib.request`), so no additional `pip` installations are required.

4.  **Running the Script**: Execute the translation script from the `AI-Translate` directory:

    ```bash
    python translate.py
    ```

    The script will prompt you to enter the English text you wish to translate. You can also type `listmodels` to see the available Gemini models. The translated text for each target language will be displayed directly in the console.