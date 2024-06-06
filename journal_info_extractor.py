import requests
from bs4 import BeautifulSoup
from gpt4all import GPT4All
import re

# Initialize the GPT-4All model (ensure the model is downloaded and available locally)
gpt4all_model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")

def extract_journal_info(text):
    # Define a prompt for the model to extract journal title and volume
    with gpt4all_model.chat_session():
        volume = gpt4all_model.generate(prompt=f"Whats the volume number here?: '{text}'", temp=0)
    return extract_number(volume)

def extract_number(text):
    # Use regex to find all numbers in the string
    numbers = re.findall(r'\d+', text)
    if numbers:
        # Assuming you want the first number found
        return numbers[0]
    else:
        return None

def process_text_for_journal_info(text):
    # This function could process multiple journal references if needed
    # Extracting journal title and volume for each reference found in the text
    journal_info = extract_journal_info(text)
    return journal_info

# Example usage
#text = '    "journal-ref": "Journal of Applied Physics, vol 104, 073536 (2008)",'
#journal_volume = process_text_for_journal_info(text)
# print(journal_volume)