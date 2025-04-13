"""
JCU Orientation Chatbot
A Flask-based chatbot application for James Cook University orientation assistance.
Handles FAQs, program inquiries, and provides AI-generated responses when needed.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ctransformers import AutoModelForCausalLM
from flask_cors import CORS
import numpy as np
import json
import re
import os

# ======================
# MODEL CONFIGURATION
# ======================
ai_model = AutoModelForCausalLM.from_pretrained(
    "models/",
    model_file="ggml-model-q4-0.bin",
    model_type="replit",
    gpu_layers=0,
    context_length=512,
    batch_size=1
)


# ======================
# DATA LOADING & PREPROCESSING
# ======================
def load_json(filename):
    """
        Load and validate JSON data from file with error handling.
        Args:
            filename (str): Path to JSON file
        Returns:
            list: Loaded intents data or empty list on failure
        """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data.get("intents", []), list):
                raise ValueError("Invalid JSON structure")
            return data["intents"]
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return []


# Load all knowledge databases
databases = {
    "main": load_json("main_database.json"),
    "full-time": load_json("full-time-progs_database.json"),
    "part-time": load_json("part-time-progs_database.json")
}

FEEDBACK_FILE = "feedback.json"


def save_feedback(entry):
    """
    Save user feedback to JSON file with error handling.
    Args:
        entry (dict): Feedback data including rating and comment
    """
    try:
        # Load existing feedback or initialize new list
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        # Append new entry and save
        data.append(entry)
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Failed to save feedback: {e}")


# --- Enhanced data preparation ---
def prepare_training_data():
    """
    Prepare training data from all loaded databases.
    Returns:
        tuple: (patterns, responses, tags) for vectorization
    """
    patterns, responses, tags = [], [], []

    for db_type, db in databases.items():
        for item in db:
            for pattern in item.get("patterns", []):
                patterns.append(pattern.lower())
                responses.append(item.get("responses", ["No response available."])[0])
                tags.append((db_type, item.get("tag", "")))
    return patterns, responses, tags


# Initialize training data and vectorizer
patterns, responses, tags = prepare_training_data()
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(patterns)


# ======================
# UTILITY FUNCTIONS
# ======================
def clean_input(text):
    """
    Sanitize user input by removing special chars and normalizing.
    Args:
        text (str): Raw user input
    Returns:
        str: Cleaned and normalized text
    """
    text = re.sub(r"[^\w\s]", "", text.lower().strip())
    return " ".join(text.split())


def get_ai_response(prompt, context=""):
    """
    Generate AI response using the loaded language model with safety limits.
    Args:
        prompt (str): User question
        context (str): Additional context for the model
    Returns:
        str: Generated response (limited to 150 chars)
    """
    try:
        # Create limited knowledge base
        knowledge_base = "\n".join(
            [f"Q: {p}\nA: {r}" for p, r in zip(patterns, responses[:50])])  # Limit to 50 examples

        # Construct full prompt with instructions
        full_prompt = f"""Respond briefly as a university assistant:
Context: {context}
Question: {prompt}
Knowledge: {knowledge_base}
Short Answer:"""

        # Generate and limit response
        return ai_model(
            full_prompt,
            max_new_tokens=50,  # Reduced from 100
            temperature=0.3,
            repetition_penalty=1.2
        ).strip()[:150]  # Hard length limit

    except Exception as e:
        print(f"AI Model Error: {str(e)}")
        return "I'm having trouble answering that. Please ask about orientation matters."


# ======================
# FLASK APPLICATION
# ======================
app = Flask(__name__, static_folder='static')
CORS(app)

# Predefined patterns for greetings and small talk
GREETING_PATTERNS = ["hi", "hello", "hey", "greetings", "hey there", "good morning", "good evening", "good afternoon",
                     "hola"]
GETTING_RESPONSES = [
    "Hello! Welcome to JCU Orientation. How can I help you?",
    "Hi there! Ready for your orientation? What do you need to know?"
]
SMALL_TALK = {
    "how are you": "I'm doing well, thanks! How can I help with your orientation?",
    "what's up": "Ready to help with your JCU orientation questions!",
    "thank you": "You're welcome! Is there anything else you need?"
}


# ======================
# ROUTES
# ======================
@app.route("/test-data")
def test_data():
    """Endpoint for testing data loading status"""
    return jsonify({
        "main_db_count": len(databases["main"]),
        "full_time_count": len(databases["full-time"]),
        "part_time_count": len(databases["part-time"]),
        "sample_pattern": patterns[0] if patterns else "No patterns loaded"
    })


@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)


@app.route("/")
def index():
    """Serve main index page"""
    return render_template("index.html")


# Route for Quiz
@app.route('/quiz', methods=['GET'])
def get_quiz():
    # Load the quiz data from the JSON file
    with open(os.path.join('static', 'data', 'quiz.json'), 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)
    return jsonify(quiz_data)


# Route for Emoji Game
@app.route('/emoji-game', methods=['GET'])
def get_emoji_game():
    # Load the emoji game data from the JSON file with the correct encoding
    with open(os.path.join('static', 'data', 'emoji_game.json'), 'r', encoding='utf-8') as f:
        emoji_game_data = json.load(f)
    # Return the emoji game data as JSON
    return jsonify(emoji_game_data)


# Route for FAQ
@app.route('/faq', methods=['GET'])
def get_faq():
    # Load the FAQ data from the JSON file
    with open(os.path.join('static', 'data', 'faq.json'), 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
    return jsonify(faq_data)


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint that handles user queries, feedback, and response generation.
    Returns:
        JSON response with either:
            - A direct answer
            - A request for feedback
            - An error message
    """
    try:
        data = request.json
        user_input = clean_input(data.get("query", ""))
        user_type = data.get("user_type", "").lower()

        print(f"Processing: {user_input}")  # Debug logging

        # Handle chat exit request
        if user_input in ["exit", "bye", "goodbye"]:
            return jsonify({
                "response": "Before you go, could you please rate your chat experience (1-5) and leave a comment?",
                "reset": True,
                "expect_feedback": True  # frontend uses this to show feedback UI
            })

        # Collect feedback if provided
        if data.get("feedback_rating") and data.get("feedback_comment"):
            feedback_entry = {
                "rating": int(data["feedback_rating"]),
                "comment": data["feedback_comment"],
                "user_type": user_type
            }
            save_feedback(feedback_entry)

            return jsonify({
                "response": "Thanks for your feedback! We’ll use it to improve future orientations.",
                "reset": True
            })

        # Handle greetings
        if user_input in GREETING_PATTERNS:
            return jsonify({
                "response": np.random.choice(GETTING_RESPONSES),
                "reset": False
            })

        # Handle small talk
        if user_input in SMALL_TALK:
            return jsonify({"response": SMALL_TALK[user_input], "reset": False})

        # Knowledge base matching using cosine similarity
        if patterns:
            input_vector = vectorizer.transform([user_input])
            similarities = cosine_similarity(input_vector, X)[0]
            best_match_idx = np.argmax(similarities)

            if similarities[best_match_idx] > 0.5:  # Lowered threshold
                return jsonify({
                    "response": responses[best_match_idx],
                    "reset": False
                })

        # Fallback to AI-generated response
        return jsonify({
            "response": "I can help with orientation questions. Try asking about: classes, schedules, or campus "
                        "services.",
            "reset": False
        })

    except Exception as e:
        print(f"System Error: {str(e)}")
        return jsonify({
            "response": "Our orientation team can help with that. Email info@jcu.edu.au",
            "reset": False
        })


# ======================
# MAIN ENTRY POINT
# ======================
if __name__ == "__main__":
    app.run(port=5000, debug=True)
