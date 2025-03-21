from random import random

from data_preparation import responses, preprocess, vectorizer, full_time_db, part_time_db, main_db
from model_training import model


def get_response(tag):
    return random.choice(responses[tag])


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


# Example usage
student_type = input("Are you a full-time or part-time student? (full-time/part-time): ").lower()
while True:
    user_input = input("You: ")
    if user_input.lower() in ['bye', 'goodbye', 'exit']:
        print("Chatbot: Goodbye!")
        break
    response = chatbot_response(user_input, student_type)
    print(f"Chatbot: {response}")