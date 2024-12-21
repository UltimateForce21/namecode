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



#MAIN TESTING CODE
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

# We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating
messages = [
    {
        "role": "system",
        "content": "You are a system that is imputted by the user a theme and number of words for which you just output words related to that theme that can be used for a game of codenames. You are to output just the words and nothing else. For example for the case the user enters: Fruits 5. You may output something like: Apples, Bananas, Oranges, Grapes, Pears. You will repeat a process like this for every user request of the format '<theme> <num_words>'",
    },
    {"role": "user", "content": "One Piece 15"},
]
prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])

