# Assorted Scripts

This repository contains a collection of various utility scripts designed for different purposes.

## Table of Contents

- [Translations Script](#translations-script)
  - [Setup and Usage](#setup-and-usage)


## Translations Script

The `AI-translate` directory houses a Python script (`translate.py`) designed for automated text translation. This script leverages external APIs for its translation capabilities.

### Setup and Usage

1.  **Environment Variables**: Before running the script, you need to set up your environment variables. A template is provided in `AI-translate/.env.example`. Copy this file to `AI-translate/.env` and fill in the necessary API keys and configurations.

    ```bash
    cp AI-translate/.env.example AI-translate/.env
    # Open AI-translate/.env and add your API keys
    ```

2.  **Dependencies**: Ensure you have Python installed. There are no required Python packages.

3.  **Running the Script**: Execute the translation script from the `AI-translate` directory:

    ```bash
    python AI-translate/translate.py
    ```

    Follow the on-screen prompts or refer to the script's internal documentation for specific usage instructions and parameters.

---

More scripts will be added to this repository in the future.
