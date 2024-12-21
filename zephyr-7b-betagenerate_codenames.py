from transformers import pipeline
from huggingface_hub import login

# Function to load the Hugging Face API token from a file
def load_token_from_file(token_file_path):
    try:
        with open(token_file_path, 'r') as file:
            return file.read().strip()  # Strip any extra newlines or spaces
    except Exception as e:
        print(f"Error loading token from file: {e}")
        return None

# Path to your token file (relative or absolute)
token_file_path = 'namecodestoken'

api_token = load_token_from_file(token_file_path)

# Check if token was successfully loaded
if api_token:
    login(api_token)  # Log in using the loaded token
else:
    print("Error: Could not load the API token.")



def example_chat():
    pipe = pipeline("text-generation", "HuggingFaceH4/zephyr-7b-beta")
    messages = [
        {
            "role": "system",
            "content": "You are a friendly chatbot who always responds in the style of a pirate",
        },
        {"role": "user", "content": "How many helicopters can a human eat in one sitting?"},
    ]
    print(pipe(messages, max_new_tokens=128)[0]['generated_text'][-1])  # Print the assistant's response


example_chat()