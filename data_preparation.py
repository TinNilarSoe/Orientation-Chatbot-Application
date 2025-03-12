# data_preparation.py

import json
import spacy
from googletrans import Translator

# Load JSON
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

main_db = load_json('main_database.json')
full_time_db = load_json('full-time-progs_database.json')
part_time_db = load_json('part-time-progs_database.json')

# Combine all intents
all_intents = main_db['intents'] + full_time_db['intents'] + part_time_db['intents']

# Load spaCy model
nlp = spacy.load('en_core_web_md')

# Preprocess function
def preprocess(text):
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
