import torch
from transformers import pipeline

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

# MAIN TESTING CODE
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

# Updated chat template with clearer instructions
messages = [
    {
        "role": "system",
        "content": "You are a word generator for the game Codenames. When given a theme and number in the format 'theme number', output exactly that many words related to the theme, separated by commas. Output only the words themselves with no additional text, explanation, or formatting.",
    },
    {
        "role": "user",
        "content": "fruits 2"
    },
    {
        "role": "assistant",
        "content": "Apples, Bananas"
    },
    {
        "role": "user",
        "content": "animals 3"
    },
    {
        "role": "assistant",
        "content": "Lion, Elephant, Tiger"
    },
    {
        "role": "user",
        "content": "One Piece 15"
    }
]

prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])