# Gemini Chat Script

This script (`chat_with_gemini.py`) is a Python-based tool for interactive conversations with the Gemini AI model.

## Features

*   **Interactive Menu**: Provides a menu-driven interface for various actions.
*   **Interactive Chat**: Engage in real-time conversations with the Gemini AI.
*   **Model Selection**: Allows users to select different Gemini models for conversation.
*   **Context Provision**: Ability to provide context to the AI from a local file.
*   **Response Logging**: Option to write AI responses to a specified file.
*   **Gemini API Integration**: Leverages the Gemini API for robust and intelligent responses.
*   **Configurable API Key**: API key is loaded from a `.env` file for secure and flexible configuration.
*   **Model Listing**: Allows users to list available Gemini models directly from the script.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/Gemini-Chat
    ```

2.  **Environment Variables**: Before running the script, you need to set up your environment variables. A template is provided in `.env.example`. Copy this file to `.env` and fill in the necessary API keys and configurations.

    ```bash
    cp .env.example .env
    # Open .env and add your API keys
    ```

3.  **Dependencies**: Ensure you have Python installed. This script uses standard Python libraries, so no additional `pip` installations are required.

4.  **Running the Script**: Execute the chat script from the `Gemini-Chat` directory:

    ```bash
    python chat_with_gemini.py
    ```

    The script will present a menu with several options:
    1.  **Chat with Gemini**: Start an interactive chat session. You can type your messages, and the Gemini AI will respond. Type `exit` or `quit` to end the chat session.
    2.  **List available models**: Display a list of Gemini models accessible via your API key.
    3.  **Select a model**: Change the Gemini model used for conversations.
    4.  **Provide context from a file**: Load content from a local file to provide context for the AI's responses.
    5.  **Toggle writing response to a file**: Enable or disable writing the AI's responses (specifically content within `<file_content>` tags) to a specified file.
    6.  **Exit**: Terminate the script.