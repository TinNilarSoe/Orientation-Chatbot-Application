import json
import random
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from googletrans import Translator


# Load JSON databases
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


main_db = load_json('main_database.json')
full_time_db = load_json('full-time-progs_database.json')
part_time_db = load_json('part-time-progs_database.json')

# Combine all intents for responses
all_intents = main_db['intents'] + full_time_db['intents'] + part_time_db['intents']
responses = {intent['tag']: intent['responses'] for intent in all_intents}

# Load spaCy model
nlp = spacy.load('en_core_web_md')

# Load trained model and vectorizer
with open('chatbot_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)


# Preprocess text
def preprocess(text):
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])


# Get response based on tag
def get_response(tag):
    return random.choice(responses[tag])


# Chatbot response logic
def chatbot_response(user_input, student_type):
    processed_input = preprocess(user_input)
    input_vector = vectorizer.transform([processed_input])
    predicted_tag = model.predict(input_vector)[0]

    if student_type == 'full-time':
        db = full_time_db['intents']
    elif student_type == 'part-time':
        db = part_time_db['intents']
    else:
        db = main_db['intents']

    for intent in db:
        if intent['tag'] == predicted_tag:
            return get_response(predicted_tag)

    return "I'm sorry, I don't understand that. Can you please rephrase?"


# Main interaction loop
def main():
    student_type = input("Are you a full-time or part-time student? (full-time/part-time): ").lower()
    while student_type not in ['full-time', 'part-time']:
        print("Please enter 'full-time' or 'part-time'.")
        student_type = input("Are you a full-time or part-time student? (full-time/part-time): ").lower()

    print("Chatbot: Hello! How can I assist you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['bye', 'goodbye', 'exit']:
            print("Chatbot: Goodbye! Have a great day!")
            break
        response = chatbot_response(user_input, student_type)
        print(f"Chatbot: {response}")


if __name__ == "__main__":
    main()