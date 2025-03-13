import json
from prev_ver_chatbot.model import get_response

# Load chatbot intents
def load_intents(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Main Execution
if __name__ == "__main__":
    intents = load_intents("chatbot_db.json")

    print("Chatbot is running! Type 'exit' to stop.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye!")
            break
        response = get_response(user_input, intents)
        print(f"Bot: {response}")
