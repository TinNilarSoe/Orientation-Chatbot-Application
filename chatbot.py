import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        user_input = input("You: ").strip().lower()

        if user_input in ["exit", "quit", "bye"]:
            print("See you later! Have a great time at James Cook University!")
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
