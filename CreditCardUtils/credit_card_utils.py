#!/usr/bin/env python3
"""Credit card utility tool.

Provides two utility functions selectable via command line or interactive menu:

1. Validate a credit card number using the Luhn algorithm.
2. Generate a valid credit card number from a template, where ``X`` / ``x``
   marks positions that must be filled with new digits. An optional length
   (default 16) pads the template with extra ``X`` placeholders when needed.

Examples
--------
Validate::
    python credit_card_utils.py validate 4539 1488 0343 6467

Generate (template only, length defaults to 16)::
    python credit_card_utils.py generate 4532XXXXXXXXXXXX

Generate with explicit length (template is right-padded with X up to length)::
    python credit_card_utils.py generate 4532 --length 16

Run with no arguments for an interactive menu.
"""

import argparse
import random
import sys


def luhn_checksum(sz_digits):
    """Return the Luhn checksum (0-9) for a string of digits.

    A number is valid when this checksum is 0.
    """
    n_sum = 0
    b_double = False
    # Process digits from right to left.
    for sz_char in reversed(sz_digits):
        n_digit = int(sz_char)
        if b_double:
            n_digit *= 2
            if n_digit > 9:
                n_digit -= 9
        n_sum += n_digit
        b_double = not b_double
    return n_sum % 10


def is_valid_card(sz_number):
    """Return True when ``sz_number`` is a Luhn-valid credit card number.

    Spaces and dashes are ignored. The cleaned value must contain only digits
    and be at least two digits long.
    """
    sz_clean = clean_number(sz_number)
    if len(sz_clean) < 2 or not sz_clean.isdigit():
        return False
    return luhn_checksum(sz_clean) == 0


def clean_number(sz_number):
    """Strip common separators (spaces and dashes) from a card number."""
    return sz_number.replace(" ", "").replace("-", "")


def generate_card(sz_template, n_length=16):
    """Generate a Luhn-valid card number from ``sz_template``.

    ``X`` or ``x`` characters in the template are placeholders to be filled
    with new digits. Separators (spaces/dashes) are ignored. If the cleaned
    template is shorter than ``n_length``, it is right-padded with ``X``
    placeholders. The template must not be longer than ``n_length``.

    Raises
    ------
    ValueError
        If the template contains invalid characters, is longer than
        ``n_length``, or has no placeholder available for the check digit.
    """
    if n_length < 2:
        raise ValueError("Card length must be at least 2.")

    sz_clean = clean_number(sz_template)

    # Pad with placeholders up to the requested length.
    if len(sz_clean) > n_length:
        raise ValueError(
            "Template length ({}) exceeds requested length ({}).".format(
                len(sz_clean), n_length
            )
        )
    sz_clean = sz_clean + ("X" * (n_length - len(sz_clean)))

    # Validate characters and collect placeholder positions.
    na_positions = []
    la_chars = list(sz_clean)
    for n_index, sz_char in enumerate(la_chars):
        if sz_char in ("X", "x"):
            na_positions.append(n_index)
        elif not sz_char.isdigit():
            raise ValueError(
                "Invalid character '{}' in template; only digits and X are allowed.".format(
                    sz_char
                )
            )

    if not na_positions:
        raise ValueError("Template has no X placeholders to fill.")

    # Reserve the last placeholder to compute the Luhn check digit.
    n_check_pos = na_positions.pop()

    # Fill every other placeholder with a random digit.
    for n_pos in na_positions:
        la_chars[n_pos] = str(random.randint(0, 9))

    # Solve for the reserved digit (0-9) that makes the number Luhn-valid.
    for n_candidate in range(10):
        la_chars[n_check_pos] = str(n_candidate)
        if luhn_checksum("".join(la_chars)) == 0:
            return "".join(la_chars)

    # Should never happen: a valid digit always exists for a single position.
    raise ValueError("Could not produce a valid number for the given template.")


def run_validate(sz_number):
    """Print the validation result for a card number."""
    sz_clean = clean_number(sz_number)
    if is_valid_card(sz_number):
        print("VALID: {} is a Luhn-valid credit card number.".format(sz_clean))
        return 0
    print("INVALID: {} is not a Luhn-valid credit card number.".format(sz_clean))
    return 1


def run_generate(sz_template, n_length):
    """Print a generated card number for a template and length."""
    try:
        sz_result = generate_card(sz_template, n_length)
    except ValueError as my_error:
        print("Error: {}".format(my_error), file=sys.stderr)
        return 1
    print(sz_result)
    return 0


def interactive_menu():
    """Run a simple interactive menu when no CLI arguments are given."""
    print("Credit Card Utilities")
    print("  1) Validate a credit card number")
    print("  2) Generate a valid credit card number")
    sz_choice = input("Select an option (1/2): ").strip()

    if sz_choice == "1":
        sz_number = input("Enter the credit card number: ").strip()
        return run_validate(sz_number)

    if sz_choice == "2":
        sz_template = input(
            "Enter the template (use X for new digits, e.g. 4532XXXXXXXXXXXX): "
        ).strip()
        sz_length = input("Enter the length [default 16]: ").strip()
        try:
            n_length = int(sz_length) if sz_length else 16
        except ValueError:
            print("Error: Length must be an integer.", file=sys.stderr)
            return 1
        return run_generate(sz_template, n_length)

    print("Unknown option.", file=sys.stderr)
    return 1


def build_parser():
    """Build the command line argument parser."""
    my_parser = argparse.ArgumentParser(
        description="Validate or generate credit card numbers."
    )
    my_subparsers = my_parser.add_subparsers(dest="command")

    my_validate = my_subparsers.add_parser(
        "validate", help="Validate a credit card number using the Luhn algorithm."
    )
    my_validate.add_argument(
        "number",
        nargs="+",
        help="The credit card number (spaces and dashes are allowed).",
    )

    my_generate = my_subparsers.add_parser(
        "generate", help="Generate a valid credit card number from a template."
    )
    my_generate.add_argument(
        "template",
        nargs="+",
        help="Template digits with X/x placeholders, e.g. 4532XXXXXXXXXXXX.",
    )
    my_generate.add_argument(
        "-l",
        "--length",
        type=int,
        default=16,
        help="Total length of the generated number (default: 16).",
    )

    return my_parser


def main(la_argv=None):
    """Entry point."""
    la_argv = sys.argv[1:] if la_argv is None else la_argv

    # No arguments: fall back to the interactive menu.
    if not la_argv:
        return interactive_menu()

    my_parser = build_parser()
    my_args = my_parser.parse_args(la_argv)

    if my_args.command == "validate":
        # Join allows numbers passed as separate space-delimited groups.
        return run_validate(" ".join(my_args.number))

    if my_args.command == "generate":
        return run_generate("".join(my_args.template), my_args.length)

    my_parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
