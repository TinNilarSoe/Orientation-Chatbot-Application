script.js
document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        displayMessage("You: " + userInput, "user");
        document.getElementById("user-input").value = ""; // Clear input field

        // Send the message to the backend
        fetch('http://localhost:5000/chat', {  // Replace with your API endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            displayMessage("Chatbot: " + data.response, "bot");
        })
        .catch(err => console.error("Error: ", err));
    }
}

function displayMessage(message, sender) {
    const chatBox = document.getElementById("chat-box");
    const newMessage = document.createElement("div");
    newMessage.classList.add(sender);
    newMessage.textContent = message;
    chatBox.appendChild(newMessage);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
}