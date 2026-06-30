# Credit Card Utilities

This script provides utilities for validating and generating credit card numbers using the Luhn algorithm. It can be run either via command-line arguments or through a simple interactive terminal menu.

## Features

- **Validation**: Validate credit card numbers using the Luhn algorithm. Automatically strips spaces and dashes.
- **Generation**: Generate valid credit card numbers from a template, where `X` or `x` characters act as placeholders to be filled with valid digits.
- **Interactive Menu**: Run the script without arguments to access a user-friendly command-line menu.
- **No Dependencies**: Relies entirely on the Python standard library.

## Setup and Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vitorjna/Scripts.git
   cd Scripts/CreditCardUtils
   ```

2. **Run the Script**:
   The script does not require any external dependencies.

   **Validate a Credit Card Number**:
   ```bash
   python credit_card_utils.py validate <CARD_NUMBER>
   ```
   *Note: Spaces and dashes are ignored.*
   
   Example:
   ```bash
   python credit_card_utils.py validate 4539 1488 0343 6467
   ```

   **Generate a Credit Card Number**:
   ```bash
   python credit_card_utils.py generate <TEMPLATE> [--length LENGTH]
   ```
   *Options:*
   *   `--length` / `-l`: Total length of the generated number (default: 16).
   
   Examples:
   ```bash
   # Generate using template (defaults to length 16)
   python credit_card_utils.py generate 4532XXXXXXXXXXXX

   # Generate with explicit length (pads the template with X up to the length)
   python credit_card_utils.py generate 4532 --length 16
   ```

   **Run Interactive Menu**:
   Simply run the script with no arguments:
   ```bash
   python credit_card_utils.py
   ```

## Project Structure

- `credit_card_utils.py`: The utility script containing validation and generation logic.
