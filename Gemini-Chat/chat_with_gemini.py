import json
import os
import re
import urllib.error
import urllib.request

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
DEFAULT_MODEL_NAME = "gemini-2.5-flash-preview-05-20"
# DEFAULT_MODEL_NAME = "gemma-3-27b-it"


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
        return []

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    models_info = _make_api_request(api_url)

    available_models = []

    if models_info:
        print("\n--- Available Models ---")
        for model in models_info.get("models", []):
            model_name = model.get('name')

            if model_name and ("gemini" in model_name or "gemma" in model_name):
                print(f"Name: {model_name}")
                available_models.append(model_name)
        print("-" * 30)
    return available_models


def chat_with_gemini():
    global API_KEY # Declare API_KEY as global to modify it if needed

    if not API_KEY:
        API_KEY = input("Enter your Gemini API key: ")
        print("API key can be saved to .env file for future use, but you'll need to do it manually.")

    current_model = DEFAULT_MODEL_NAME
    history = []
    file_to_write = None
    context_content = None

    print(f"Starting a conversation with Gemini using model: {current_model}.")

    while True:
        print("\n--- Menu ---")
        print("1. Chat with Gemini (type exit or quit to end)")
        print("2. List available models")
        print("3. Select a model")
        print("4. Provide context from a file")
        print(f"5. Toggle writing response to a file (Current: {'ON' if file_to_write else 'OFF'})")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation.")
                break

            GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={API_KEY}"

            # Prepare content for the model, including context if available
            content_parts = [{"text": user_input}]

            if context_content:
                content_parts.insert(0, {"text": f"Context: {context_content}\n\n"})
                context_content = None # Clear context after use

            history.append({"role": "user", "parts": content_parts})

            payload = {
                "contents": history,
                "generationConfig": {
                    "temperature": 0.9,
                    "topP": 1,
                    "topK": 1,
                    "maxOutputTokens": 2048,
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            }

            response_json = _make_api_request(GEMINI_API_URL, method='POST', data=json.dumps(payload).encode('utf-8'))

            if response_json:

                if "candidates" in response_json and response_json["candidates"]:
                    gemini_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"Gemini: {gemini_text}")
                    history.append({"role": "model", "parts": [{"text": gemini_text}]})

                    if file_to_write:
                        # Extract content between <file_content> tags
                        match = re.search(r"<file_content>(.*?)</file_content>", gemini_text, re.DOTALL)

                        if match:
                            content_to_write = match.group(1).strip()
                            try:
                                with open(file_to_write, 'w') as f:
                                    f.write(content_to_write)
                                print(f"Successfully wrote content to {file_to_write}")

                            except IOError as e:
                                print(f"Error writing to file {file_to_write}: {e}")

                        else:
                            print("No <file_content> tags found in the model's response.")

                elif "promptFeedback" in response_json and "blockReason" in response_json["promptFeedback"]:
                    print(f"Gemini: Your prompt was blocked due to: {response_json['promptFeedback']['blockReason']}")

                else:
                    print("Gemini: No response received or an unexpected format.")

            else:
                print("Gemini: Failed to get a response from the API.")

        elif choice == '2':
            list_models()

        elif choice == '3':
            new_model = input("Enter the new model name: ").strip()

            if new_model:
                current_model = new_model
                print(f"Model changed to: {current_model}")

            else:
                print("Model name cannot be empty.")

        elif choice == '4':
            context_file_path = input("Enter the path to the context file: ").strip()

            if context_file_path:
                try:
                    with open(context_file_path, 'r') as f:
                        context_content = f.read()
                    print(f"Loaded content from {context_file_path} as context.")

                except FileNotFoundError:
                    print(f"Error: Context file not found at {context_file_path}")
                    context_content = None

                except Exception as e:
                    print(f"Error reading context file {context_file_path}: {e}")
                    context_content = None

            else:
                print("Context file path cannot be empty.")

        elif choice == '5':
            if file_to_write:
                print(f"Stopping writing responses to {file_to_write}.")
                file_to_write = None
                # Send a message to the model to stop using tags
                history.append({"role": "user", "parts": [{"text": "I got what I needed for my file, you don't have to use file_content tags anymore"}]})

            else:
                file_to_write_path = input("Enter the file path to write responses to: ").strip()

                if file_to_write_path:
                    file_to_write = file_to_write_path
                    print(f"Entering write file mode. Model response will be written to {file_to_write} if tagged.")
                    # Send a message to the model to start using tags
                    history.append({"role": "user", "parts": [{"text": "I want your next answers to be written to a file. Please use <file_content>...</file_content> tags and everything within the tags will be written to the file."}]})

                else:
                    print("File path for writing cannot be empty.")

        elif choice == '6':
            print("Ending conversation.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    chat_with_gemini()