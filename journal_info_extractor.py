import requests
from bs4 import BeautifulSoup
from gpt4all import GPT4All
import re

gpt4all_model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")

def extract_journal_info(text):
    with gpt4all_model.chat_session():
        volume = gpt4all_model.generate(prompt=f"Whats the volume number here?: '{text}'", temp=0)
    return extract_number(volume)

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return numbers[0]
    else:
        return None

def process_text_for_journal_info(text):
    journal_info = extract_journal_info(text)
    return journal_info

# Example usage
text = '    "journal-ref": "Journal of Applied Physics, vol 104, 073536 (2008)",'
journal_volume = process_text_for_journal_info(text)
print(journal_volume)