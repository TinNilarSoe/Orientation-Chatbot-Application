import json
import random
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator

# Load English NLP model
nlp = spacy.load("en_core_web_md")
translator = Translator()

# Load chatbot intents
def load_intents(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Convert sentence into vector using spaCy embeddings
def get_sentence_vector(sentence):
    return nlp(sentence).vector.reshape(1, -1)

# Find best-matching intent using similarity
def get_best_intent(user_input, intents):
    user_vector = get_sentence_vector(user_input)
    best_match = None
    highest_similarity = 0.0

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            pattern_vector = get_sentence_vector(pattern)
            similarity = cosine_similarity(user_vector, pattern_vector)[0][0]

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = intent

    return best_match if highest_similarity > 0.6 else None  # Adjust threshold as needed

# Translate non-English input to English
def translate_to_english(text):
    detected_lang = translator.detect(text).lang
    if detected_lang != "en":
        translated_text = translator.translate(text, dest="en").text
        return translated_text
    return text

# Function to find best-matching response
def get_response(user_input, intents):
    user_input = translate_to_english(user_input.lower().strip())  # Translate & Normalize

    best_intent = get_best_intent(user_input, intents)
    if best_intent:
        return random.choice(best_intent["responses"])  # Select random response

    return "Sorry, I don't understand that. Could you rephrase?"

# Main Execution
if __name__ == "__main__":
    intents = load_intents("chatbot_db.json")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye!")
            break
        response = get_response(user_input, intents)
        print(f"Bot: {response}")
