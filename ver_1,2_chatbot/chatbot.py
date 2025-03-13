import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator

translator = Translator()


switch_keywords = ["switch to full-time", "switch to part-time", "change to full-time", "change to part-time",
                   "i'm a full-time student now", "i'm part-time now"]


# Load JSON databases
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


main_db = load_json("main_database.json")["intents"]
full_time_db = load_json("full-time-progs_database.json")["intents"]
part_time_db = load_json("part-time-progs_database.json")["intents"]


# Combine all patterns for training
def prepare_training_data(databases):
    patterns, tags = [], []

    for db in databases:
        for item in db:
            for pattern in item["patterns"]:
                patterns.append(pattern)
                tags.append(item["tag"])

    return patterns, tags


# Train TF-IDF model
def train_nlp_model():
    all_patterns, all_tags = prepare_training_data([main_db, full_time_db, part_time_db])

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(all_patterns)

    return vectorizer, X, all_patterns, all_tags


vectorizer, X, all_patterns, all_tags = train_nlp_model()


# Function to find the best matching tag using cosine similarity
def find_best_match(user_input):
    user_input_vector = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_input_vector, X).flatten()

    best_match_idx = np.argmax(similarities)
    confidence = similarities[best_match_idx]

    if confidence > 0.3:  # Adjust threshold as needed
        return all_tags[best_match_idx]
    else:
        return None

def translate_to_english(text):
    try:
        detected = translator.detect(text).lang
        if detected != 'en':
            translated = translator.translate(text, src=detected, dest='en')
            return translated.text.lower()
        return text.lower()
    except Exception as e:
        print("Translation error:", e)
        return text.lower()

# Function to get response from the appropriate database
def get_response(tag, selected_db):
    # Check main_db and selected_db (either full_time_db or part_time_db)
    for item in main_db + selected_db:
        if item["tag"] == tag:
            return random.choice(item["responses"]) if isinstance(item["responses"], list) else item["responses"]
    return "I'm sorry, I don't have information on that."


# Main chatbot function
def chatbot():
    print("Welcome to the Student Orientation Chatbot!")
    print("Are you a Full-time or Part-time student? (Type 'full-time' or 'part-time')")

    # Choose database
    while True:
        user_type = input("You: ").strip().lower()
        if user_type in ["full-time", "part-time"]:
            selected_db = full_time_db if user_type == "full-time" else part_time_db
            print(f"Great! You're a {user_type} student. How can I help you?")
            break
        else:
            print("Please enter 'full-time' or 'part-time'.")

    # Chat loop
    while True:
        original_input = input("You: ").strip()
        user_input = translate_to_english(original_input)

        # Check if user wants to switch student type
        if any(keyword in user_input for keyword in switch_keywords):
            if "full-time" in user_input:
                selected_db = full_time_db
                print("Got it! You've switched to Full-time student mode. How can I help you now?")
            elif "part-time" in user_input:
                selected_db = part_time_db
                print("Got it! You've switched to Part-time student mode. How can I help you now?")
            continue

        if user_input in ["exit", "quit", "bye"]:
            print("Goodbye! Have a great day.")
            break

        tag = find_best_match(user_input)

        if tag:
            response = get_response(tag, selected_db)
        else:
            response = "Sorry, I couldn't understand that. Could you rephrase?"

        print("Bot:", response)


# Run chatbot
if __name__ == "__main__":
    chatbot()