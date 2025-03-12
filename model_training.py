# model_training.py

import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Load JSON databases
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

main_db = load_json('main_database.json')
full_time_db = load_json('full-time-progs_database.json')
part_time_db = load_json('part-time-progs_database.json')

# Combine all intents
all_intents = main_db['intents'] + full_time_db['intents'] + part_time_db['intents']

# Extract patterns and tags
patterns = []
tags = []

for intent in all_intents:
    for pattern in intent['patterns']:
        patterns.append(pattern)
        tags.append(intent['tag'])

# Preprocessing
def preprocess(text):
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

processed_patterns = [preprocess(p) for p in patterns]

# Vectorize
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(processed_patterns)
y = tags

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict & evaluate
y_pred = model.predict(X_test)
print("Model accuracy:", accuracy_score(y_test, y_pred))
print("Classification report:\n", classification_report(y_test, y_pred))

# Save model and vectorizer
with open('chatbot_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
