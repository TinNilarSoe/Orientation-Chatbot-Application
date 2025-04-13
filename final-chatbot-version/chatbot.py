import json
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from ctransformers import AutoModelForCausalLM
import numpy as np

# Modify your model initialization:
ai_model = AutoModelForCausalLM.from_pretrained(
    "models/",
    model_file="ggml-model-q4-0.bin",
    model_type="replit",
    gpu_layers=0,
    context_length=512,  # Reduce from default 2048
    batch_size=1        # Process one at a time
)


# --- Enhanced JSON loading with validation ---
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data.get("intents", []), list):
                raise ValueError("Invalid JSON structure")
            return data["intents"]
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return []


# Load all databases
databases = {
    "main": load_json("main_database.json"),
    "full-time": load_json("full-time-progs_database.json"),
    "part-time": load_json("part-time-progs_database.json")
}


# --- Enhanced data preparation ---
def prepare_training_data():
    patterns, responses, tags = [], [], []
    for db_type, db in databases.items():
        for item in db:
            for pattern in item.get("patterns", []):
                patterns.append(pattern.lower())
                responses.append(item.get("responses", ["No response available."])[0])
                tags.append((db_type, item.get("tag", "")))
    return patterns, responses, tags


patterns, responses, tags = prepare_training_data()
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(patterns)


# --- Input sanitization ---
def clean_input(text):
    text = re.sub(r"[^\w\s]", "", text.lower().strip())
    return " ".join(text.split())


# --- Enhanced AI response generation ---
# Replace your get_ai_response function with this safer version:
def get_ai_response(prompt, context=""):
    try:
        knowledge_base = "\n".join(
            [f"Q: {p}\nA: {r}" for p, r in zip(patterns, responses[:50])])  # Limit to 50 examples

        full_prompt = f"""Respond briefly as a university assistant:
Context: {context}
Question: {prompt}
Knowledge: {knowledge_base}
Short Answer:"""

        return ai_model(
            full_prompt,
            max_new_tokens=50,  # Reduced from 100
            temperature=0.3,
            repetition_penalty=1.2
        ).strip()[:150]  # Hard length limit

    except Exception as e:
        print(f"AI Model Error: {str(e)}")
        return "I'm having trouble answering that. Please ask about orientation matters."

# Flask setup
app = Flask(__name__, static_folder='static')
CORS(app)

@app.route("/test-data")
def test_data():
    return jsonify({
        "main_db_count": len(databases["main"]),
        "full_time_count": len(databases["full-time"]),
        "part_time_count": len(databases["part-time"]),
        "sample_pattern": patterns[0] if patterns else "No patterns loaded"
    })

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route("/")
def index():
    return render_template("index.html")


# Add this near the top after loading patterns
greeting_patterns = ["hi", "hello", "hey", "greetings"]
greeting_responses = [
    "Hello! Welcome to JCU Orientation. How can I help you?",
    "Hi there! Ready for your orientation? What do you need to know?"
]


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_input = clean_input(data.get("query", ""))
        user_type = data.get("user_type", "").lower()

        print(f"Processing: {user_input}")  # Debug logging

        # Handle greetings
        if user_input in greeting_patterns:
            return jsonify({
                "response": np.random.choice(greeting_responses),
                "reset": False
            })

        # Simple responses for common small talk
        small_talk = {
            "how are you": "I'm doing well, thanks! How can I help with your orientation?",
            "what's up": "Ready to help with your JCU orientation questions!",
            "thank you": "You're welcome! Is there anything else you need?"
        }

        if user_input in small_talk:
            return jsonify({"response": small_talk[user_input], "reset": False})

        # Knowledge base matching
        if patterns:
            input_vector = vectorizer.transform([user_input])
            similarities = cosine_similarity(input_vector, X)[0]
            best_match_idx = np.argmax(similarities)

            if similarities[best_match_idx] > 0.5:  # Lowered threshold
                return jsonify({
                    "response": responses[best_match_idx],
                    "reset": False
                })

        # Fallback response
        return jsonify({
            "response": "I can help with orientation questions. Try asking about: classes, schedules, or campus services.",
            "reset": False
        })

    except Exception as e:
        print(f"System Error: {str(e)}")
        return jsonify({
            "response": "Our orientation team can help with that. Email info@jcu.edu.au",
            "reset": False
        })

if __name__ == "__main__":
    app.run(port=5000, debug=True)