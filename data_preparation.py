import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from googletrans import Translator

# Load JSON databases
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

main_db = load_json('main_database.json')
full_time_db = load_json('full-time-progs_database.json')
part_time_db = load_json('part-time-progs_database.json')

# Combine all intents for training
all_intents = main_db['intents'] + full_time_db['intents'] + part_time_db['intents']

# Prepare training data
patterns = []
tags = []
responses = {}

for intent in all_intents:
    tag = intent['tag']
    responses[tag] = intent['responses']
    for pattern in intent['patterns']:
        patterns.append(pattern)
        tags.append(tag)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Initialize translator
translator = Translator()

# Preprocess text
def preprocess(text):
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

processed_patterns = [preprocess(pattern) for pattern in patterns]

# Vectorize patterns
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(processed_patterns)