from flask import Flask, request, jsonify
from chatbot_logic import chatbot_response

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')

    # Get the chatbot's response based on user input
    response = chatbot_response(user_input)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)