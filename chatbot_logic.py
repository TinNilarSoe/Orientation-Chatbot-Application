# chatbot_logic.py

from data_preparation import preprocess, full_time_db, part_time_db, main_db
import pickle
import random

# Load model & vectorizer
with open('chatbot_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Combine all responses into dict
all_intents = main_db['intents'] + full_time_db['intents'] + part_time_db['intents']
responses = {intent['tag']: intent['responses'] for intent in all_intents}

def get_response(tag):
    return random.choice(responses.get(tag, ["Sorry, I couldn't find a proper response."]))

def chatbot_response(user_input):
    processed_input = preprocess(user_input)
    input_vector = vectorizer.transform([processed_input])
    predicted_tag = model.predict(input_vector)[0]
    return get_response(predicted_tag)

# Example loop
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        response = chatbot_response(user_input)
        print("Chatbot:", response)
