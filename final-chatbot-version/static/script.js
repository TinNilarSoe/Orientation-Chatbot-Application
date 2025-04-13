const chatbotContainer = document.getElementById('chatbot-container');
const chatbotButton = document.getElementById('chatbot-button');
const messagesDiv = document.getElementById('chatbot-messages');
const userInputField = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const typeButtons = document.getElementById('type-buttons');

let userType = null;
let welcomeMessageShown = false;

// Toggle the chatbot window
chatbotButton.onclick = function (event) {
    event.stopPropagation();
    chatbotContainer.style.display = chatbotContainer.style.display === 'none' ? 'flex' : 'none';
    chatbotButton.classList.toggle('hidden', chatbotContainer.style.display === 'flex');
    if (chatbotContainer.style.display === 'flex' && !welcomeMessageShown && userType === null) {
        askUserType();
        welcomeMessageShown = true;
    }
};

// Close the chat window when clicking outside
document.addEventListener('click', function (event) {
    if (!chatbotContainer.contains(event.target) && !chatbotButton.contains(event.target)) {
        chatbotContainer.style.display = 'none';
        chatbotButton.classList.remove('hidden');
    }
});

function askUserType() {
    addMessage("Welcome to the Student Orientation Chatbot! Are you a full-time or part-time student?", 'bot');

    // Hide input area
    document.getElementById('input-area').classList.add('hidden');

    // Create buttons overlay
    typeButtons.innerHTML = `
        <div class="type-overlay">
            <button class="type-btn full-time-btn">Full-time</button>
            <button class="type-btn part-time-btn">Part-time</button>
        </div>
    `;

    // Add button event listeners
    document.querySelector('.full-time-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        setUserType('full-time');
    });
    document.querySelector('.part-time-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        setUserType('part-time');
    });
}

function setUserType(type) {
    userType = type;
    typeButtons.innerHTML = ''; // Remove buttons overlay
    document.getElementById('input-area').classList.remove('hidden'); // Show input area
    addMessage(Great! You're a ${type} student. How can I help you?, 'bot');
}

// Add messages to the chat window
function addMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    messageElement.appendChild(avatar);

    const text = document.createElement('div');
    text.classList.add('text');
    text.innerHTML = message;
    messageElement.appendChild(text);

    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// // Handle user input
// userInputField.addEventListener('input', function () {
//     this.style.height = 'auto';
//     this.style.height = (this.scrollHeight) + 'px';
// });
userInputField.addEventListener('input', function () {
    this.style.height = 'auto';
    const baseHeight = 38; // Matches min-height
    const newHeight = Math.min(Math.max(this.scrollHeight, baseHeight), 80);
    this.style.height = newHeight + 'px';

    // Adjust button alignment
    const inputArea = document.getElementById('input-area');
    inputArea.style.alignItems = newHeight > baseHeight ? 'flex-start' : 'center';
});


// Send message on Enter key or send button click
function sendMessage() {
    if (userInputField.value.trim() !== '' && userType !== null) {
        const userInput = userInputField.value.trim();
        userInputField.value = '';
        userInputField.style.height = 'auto';

        addMessage(userInput, 'user');
        askQuestion(userInput);
    }
}

userInputField.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendButton.addEventListener('click', sendMessage);

// Function to communicate with the Flask backend
async function askQuestion(userInput) {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: userInput,
                user_type: userType
            })
        });

        const data = await response.json();
        addMessage(data.response, 'bot');

        if (data.reset) {
            userType = null;
            welcomeMessageShown = false;
        }
    } catch (error) {
        addMessage("Sorry, something went wrong. Please try again later.", 'bot');
        console.error('Error:', error);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    // === Feedback logic ===
    let currentRating = 0;

    function showFeedbackFormInline() {
        addMessage('We’d love your feedback! Please rate this chat below:', 'bot');

        const feedbackWrapper = document.createElement('div');
        feedbackWrapper.className = 'feedback-inline';

        // Stars
        const stars = document.createElement('div');
        stars.className = 'inline-stars';
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('span');
            star.textContent = '★';
            star.dataset.value = i;
            star.style.cursor = 'pointer';
            star.style.fontSize = '20px';
            star.style.color = '#ccc'; // Default color

            // Hover effect
            star.addEventListener('mouseover', () => {
                const hoverValue = parseInt(star.dataset.value);
                [...stars.children].forEach(s => {
                    const starValue = parseInt(s.dataset.value);
                    s.style.color = starValue <= hoverValue ? 'gold' : '#ccc';
                });
            });

            // Click effect
            star.onclick = () => {
                currentRating = parseInt(star.dataset.value);
                [...stars.children].forEach(s => {
                    const starValue = parseInt(s.dataset.value);
                    s.style.color = starValue <= currentRating ? 'gold' : '#ccc';
                });
            };

            stars.appendChild(star);
        }

        // Comment box
        const commentBox = document.createElement('textarea');
        commentBox.rows = 3;
        commentBox.placeholder = 'Leave a comment...';
        commentBox.style.width = '100%';
        commentBox.style.marginTop = '5px';

        // Submit button
        const submitBtn = document.createElement('button');
        submitBtn.textContent = 'Submit Feedback';
        submitBtn.style.marginTop = '5px';
        submitBtn.onclick = async () => {
            const comment = commentBox.value.trim();
            if (!currentRating || comment === '') {
                alert('Please select a rating and write a comment!');
                return;
            }

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: 'feedback',
                        feedback_rating: currentRating,
                        feedback_comment: comment,
                        user_type: userType || 'unknown'
                    })
                });

                const data = await response.json();
                addMessage(data.response || 'Thanks for your feedback!', 'bot');
                feedbackWrapper.remove();
            } catch (err) {
                console.error('Feedback submit error:', err);
                addMessage('Error sending feedback. Try again later.', 'bot');
            }
        };

        // Add to wrapper
        feedbackWrapper.appendChild(stars);
        feedbackWrapper.appendChild(commentBox);
        feedbackWrapper.appendChild(submitBtn);

        // Append inside chat
        messagesDiv.appendChild(feedbackWrapper);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Attach to the chatbot response
    const originalAskQuestion = askQuestion;
    askQuestion = async function (userInput) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: userInput,
                    user_type: userType
                })
            });

            const data = await response.json();
            addMessage(data.response, 'bot');

            if (data.reset) {
                userType = null;
                welcomeMessageShown = false;
            }

            if (data.expect_feedback) {
                showFeedbackFormInline();
            }

        } catch (error) {
            addMessage("Sorry, something went wrong. Please try again later.", 'bot');
            console.error('Error:', error);
        }
    };
});