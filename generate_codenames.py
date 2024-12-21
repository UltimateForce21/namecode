import torch
from transformers import pipeline

# Function to load the Hugging Face API token from a file
def load_token_from_file(token_file_path):
    try:
        with open(token_file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error loading token from file: {e}")
        return None

# Path to your token file (relative or absolute)
token_file_path = 'namecodestoken'

api_token = load_token_from_file(token_file_path)

# MAIN TESTING CODE
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")


system_prompt = (
    "You are a word generator for the game Codenames. When given a theme and number "
    "in the format 'theme number', output EXACTLY that many UNIQUE words or phrases "
    "related to the theme, separated by commas. For TV shows, movies, or other media, "
    "include a diverse mix of: characters, locations, objects, concepts, story arcs, "
    "events, and themes. Remove the articles like 'the' from the start. For example, "
    "say 'Thousand Sunny' not 'The Thousand Sunny'. Keep phrases concise and direct. Never "
    "repeat words or phrases in your response. Output upto only the requested number of items with no additional text."
)




""" prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, 
              max_new_tokens=100,
              do_sample=True, 
              temperature=0.7, 
              top_k=50, 
              top_p=0.95,
              pad_token_id=pipe.tokenizer.eos_token_id)
print(outputs[0]["generated_text"]) """

def generate_words_from_theme(theme, count):
   
    # Updated chat template with cleaner output format
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": "fruits 2"
        },
        {
            "role": "assistant",
            "content": "Apple, Banana"
        },
        {
            "role": "user",
            "content": "Star Wars 5"
        },
        {
            "role": "assistant",
            "content": "Lightsaber, Tatooine, Force, Vader, Millennium-Falcon"
        },
        {
            "role": "user",
            "content": "One Piece 5"
        },
        {
            "role": "assistant",
            "content": "Pirate, Devil-Fruit, Grand-Line, Nakama, Log-Pose"
        },
        {
            "role": "user",
            "content": "One Piece 5"
        },
        {
            "role": "user",
            "content": f"{theme} {count}"
        }
    ]
    
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, 
                  max_new_tokens=100,
                  do_sample=True, 
                  temperature=0.7, 
                  top_k=50, 
                  top_p=0.95,
                  pad_token_id=pipe.tokenizer.eos_token_id)
    
    # Extract and clean the generated words
    generated_text = outputs[0]["generated_text"]
    print(generated_text)
    
    # Find the last assistant message more reliably
    parts = generated_text.split("<|assistant|>")
    if len(parts) > 1:
        assistant_response = parts[-1].split("</s>")[0].strip()
        # Split by commas and clean each word
        words = [word.strip() for word in assistant_response.split(',') if word.strip()]
        return words[:count]  # Ensure we only return the requested number of words
    else:
        raise Exception("Failed to generate words from theme")