import json
import random


# Load chatbot intents
def load_intents(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Function to find best-matching intent and return a random response
def get_response(user_input, intents):
    user_input = user_input.lower().strip()  # Convert to lowercase and remove extra spaces

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            pattern_lower = pattern.lower().strip()

            # Use a looser search method
            if pattern_lower in user_input:
                return random.choice(intent["responses"])  # Select a random response

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
