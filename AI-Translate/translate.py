import json
import urllib.error
import urllib.request
import os

def load_env_variable(file_path, key):
    """
    Loads a specific environment variable from a .env file.
    """
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    if k == key:
                        return v
    except FileNotFoundError:
        print(f"Error: .env file not found at {file_path}")
    except Exception as e:
        print(f"Error loading .env file: {e}")
    return None

API_KEY = load_env_variable(f"{os.path.dirname(__file__)}/.env", "GEMINI_API_TOKEN")
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
#MODEL_NAME = "gemma-3-27b-it"

def call_gemini_api(contents):
    """
    Makes a call to the Gemini API with the given contents.

    Args:
        contents (list): A list of content parts for the API request.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    if not API_KEY:
        print(f"Warning: API_KEY is not set. The call might fail if an API key is required for {MODEL_NAME}.")

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2, # Lower temperature for more deterministic translations
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 4096,
        }
    }

    json_payload = json.dumps(payload).encode('utf-8')
    return _make_api_request(api_url, method='POST', data=json_payload)

def _make_api_request(url, method='GET', data=None):
    """
    Helper function to make API requests and handle common errors.
    """
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8')
        print(f"HTTP Error: {e.code} {e.reason}\nDetails: {error_content}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except json.JSONDecodeError:
        print(f"JSON Decode Error: Could not decode JSON response.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return None

def list_models():
    """
    Lists available models from the Gemini API.
    """
    if not API_KEY:
        print("Warning: API_KEY is not set. Cannot list models without an API key.")
        return

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    models_info = _make_api_request(api_url)

    if models_info:
        print("\n--- Available Models ---")
        for model in models_info.get("models", []):
            if "2.5" in model.get('name') or "gemma" in model.get('name'):
                print(f"Name: {model.get('name')}")
#                print(f"  DisplayName: {model.get('displayName')}")
#                print(f"  Description: {model.get('description')}")
#                print(f"  InputTokenLimit: {model.get('inputTokenLimit')}")
#                print(f"  OutputTokenLimit: {model.get('outputTokenLimit')}")
#                print(f"  SupportedGenerationMethods: {', '.join(model.get('supportedGenerationMethods', []))}")
#                print("-" * 30)
#            print("\n" + "-" * 50)

def main():
    """
    Main function to get user input and perform translations.
    """
    print("Multi-Language POS Text Translator using Gemini API")
    print("-" * 50)

    user_input = input("Enter the English text you want to translate (type 'listmodels' to see available models):\n")

    if not user_input.strip():
        print("No text provided. Exiting.")
        return

    if user_input.lower() == "listmodels":
        list_models()
        return

    # Define the target languages
    target_languages = {
        "Czech":        "cs",
        "Danish":       "da",
        "German":       "de",
        "Greek":        "el",
        "English":      "en",
        "Spanish":      "es",
        "Estonian":     "et",
        "Finnish":      "fi",
        "French":       "fr",
        "Hebrew":       "he",
        "Croatian":     "hr",
        "Hungarian":    "hu",
        "Icelandic":    "is",
        "Italian":      "it",
        "Korean":       "ko",
        "Latvian":      "lv",
        "Dutch":        "nl",
        "Norwegian":    "no",
        "Polish":       "pl",
        "Portuguese":   "pt",
        "Russian":      "ru",
        "Slovak":       "sk",
        "Slovenian":    "sl",
        "Swedish":      "sv",
        "Turkish":      "tr",
    }

    # Construct a single prompt for all translations
    translation_requests = [f"- {lang_name} (Code: {lang_code})" for lang_name, lang_code in target_languages.items()]

    prompt = (
        f"Translate the following English text to the specified languages, using their ISO 639-1 codes for the translation. "
        f"The text will be displayed on a Point of Sale (POS) terminal screen, "
        f"so the translation must be concise and use common terminology for payments and card handling. "
        f"For each language, output only the translated text, prefixed with the language name and a colon, like 'Language: Translated Text'. "
        f"Do not include any other introductory or concluding remarks.\n\n"
        f"Original English Text: {user_input}\n\n"
        f"Target Languages:\n" + "\n".join(translation_requests)
    )

    contents = [{"parts": [{"text": prompt}]}]

    print("\nCalling API")
    response = call_gemini_api(contents)

    print("\n--- Translations ---")
    if response and response.get("candidates"):
        translated_content = response["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Assuming the model returns translations in the requested format,
        # we can split by lines and print them.
        for line in translated_content.split('\n'):
            print(line)
    else:
        print("Error: Could not retrieve translations from API response.")

    print("\n" + "-" * 50)
    print("Process finished.")

if __name__ == "__main__":
    main()
