import json
import random
import numpy as np
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from googletrans import Translator

translator = Translator()
switch_keywords = {
    "full-time": [
        "switch to full-time", "change to full-time", "i'm a full-time student"
    ],
    "part-time": [
        "switch to part-time", "change to part-time", "i'm a part-time student"
    ]
}


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


# Initialize Flask app
app = Flask(__name__)

# Enable CORS to allow cross-origin requests (necessary for local testing)
CORS(app)


# Serve the HTML page
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("query", "").strip()
    user_type = data.get("user_type", "").strip()

    detected = translator.detect(user_input)
    user_lang = detected.lang

    translated_input = translator.translate(user_input, src=user_lang, dest="en").text.lower()

    if translated_input in ["exit", "quit", "bye"]:
        response = "See you later! Have a great time at James Cook University!"
        translated_response = translator.translate(response, src="en", dest=user_lang).text
        return jsonify({"response": translated_response, "reset": True})

    for mode, keywords in switch_keywords.items():
        if any(kw in translated_input for kw in keywords):
            new_type = mode
            response = f"Got it! You are now set as a {new_type} student."
            translated_response = translator.translate(response, src="en", dest=user_lang).text
            return jsonify({"response": translated_response, "reset": False, "new_type": new_type})

    if user_type == "full-time":
        selected_db = full_time_db
    elif user_type == "part-time":
        selected_db = part_time_db
    else:
        response = "Please select a valid student type (full-time or part-time)."
        translated_response = translator.translate(response, src="en", dest=user_lang).text
        return jsonify({"response": translated_response})

    tag = find_best_match(translated_input)

    if tag:
        response = get_response(tag, selected_db)
    else:
        response = "Sorry, I couldn't understand that. Could you rephrase?"

    translated_response = translator.translate(response, src="en", dest=user_lang).text
    return jsonify({"response": translated_response, "reset": False})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
