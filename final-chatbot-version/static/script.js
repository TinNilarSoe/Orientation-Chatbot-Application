const chatbotContainer = document.getElementById('chatbot-container');
const chatbotButton = document.getElementById('chatbot-button');
const messagesDiv = document.getElementById('chatbot-messages');
const userInputField = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const typeButtons = document.getElementById('type-buttons');
// Games Elements
const contentContainer = document.getElementById('content-container');
const gameContent = document.getElementById('game-content');
const gameTitle = document.getElementById('game-title');
const closeGameButton = document.getElementById('close-game');

// Game buttons
const quizBtn = document.getElementById('quizBtn');
const emojiBtn = document.getElementById('emojiBtn');
const faqBtn = document.getElementById('faqBtn');

// Game data
let quizData = [];
let emojiGameData = [];
let faqData = [];

// Current game state
let currentGame = null;
let currentQuestionIndex = 0;
let score = 0;

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
    addMessage(`Great! You're a ${type} student. How can I help you?`, 'bot');
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


userInputField.addEventListener('input', function () {
    this.style.height = 'auto';
    const baseHeight = 38; // Matches min-height
    const newHeight = Math.min(Math.max(this.scrollHeight, baseHeight), 80);
    this.style.height = newHeight + 'px';

    // Adjust button alignment
    const inputArea = document.getElementById('input-area');
    inputArea.style.alignItems = newHeight > baseHeight ? 'flex-start' : 'center';
});


// Close game
closeGameButton.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling
    contentContainer.style.display = 'none';
    currentGame = null;
    currentQuestionIndex = 0;
    score = 0;
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
                    headers: {'Content-Type': 'application/json'},
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

                // Reset chatbot after feedback
                messagesDiv.innerHTML = ''; // Clear all chat history
                chatbotContainer.style.display = 'none'; // Close chatbot
                chatbotButton.classList.remove('hidden'); // Show chatbot icon
                userType = null;
                welcomeMessageShown = false;

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


// ==================== QUIZ FUNCTIONALITY ====================

// Quiz Button Click Handler
quizBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling

    currentGame = 'quiz';
    gameTitle.textContent = 'JCU Knowledge Quiz';
    contentContainer.style.display = 'flex';
    gameContent.innerHTML = '<div class="loading">Loading quiz...</div>';

    // Fetch quiz data
    fetch('/quiz')
        .then(response => response.json())
        .then(data => {
            quizData = data;
            startQuiz();
        })
        .catch(error => {
            console.error('Error loading quiz:', error);
            gameContent.innerHTML = '<div class="error">Failed to load quiz. Please try again.</div>';
        });
});

// Start Quiz
function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    displayQuizQuestion();
}

// Display Current Quiz Question
function displayQuizQuestion() {
    if (currentQuestionIndex >= quizData.length) {
        showQuizCompletion();
        return;
    }

    const question = quizData[currentQuestionIndex];

    // Create progress dots
    let progressHTML = '<div class="progress-indicator">';
    for (let i = 0; i < quizData.length; i++) {
        let dotClass = i < currentQuestionIndex ? 'completed' : (i === currentQuestionIndex ? 'active' : '');
        progressHTML += `<div class="progress-dot ${dotClass}"></div>`;
    }
    progressHTML += '</div>';

    // Create question and options HTML
    let html = `
        ${progressHTML}
        <div class="quiz-question" data-index="${currentQuestionIndex}">
            <div class="quiz-question-text">${question.question}</div>
            <div class="quiz-options">
    `;

    // Add options
    question.options.forEach((option, index) => {
       html += `<div class="quiz-option" data-option="${index}">${option}</div>`;
    });

    html += `
            </div>
        </div>
    `;

    gameContent.innerHTML = html;

    // Add event listeners to options
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', handleQuizOptionClick);
    });
}

// Handle Quiz Option Click
function handleQuizOptionClick(e) {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling

    if (document.querySelector('.feedback-message')) return; // Prevent multiple clicks

    const selectedOption = e.currentTarget;
    const optionIndex = selectedOption.getAttribute('data-option');
    const questionIndex = selectedOption.parentElement.parentElement.getAttribute('data-index');
    const question = quizData[questionIndex];
    const correctAnswerIndex = question.options.indexOf(question.answer);

    // Mark selected option
    selectedOption.classList.add('selected');

    // Check if correct
    const isCorrect = question.options[parseInt(optionIndex)] === question.answer;

    // Show correct and incorrect options
    document.querySelectorAll('.quiz-option').forEach((option, index) => {
        if (index === correctAnswerIndex) {
            option.classList.add('correct');
        } else if (index === parseInt(optionIndex) && !isCorrect) {
            option.classList.add('incorrect');
        }
    });

    // Show feedback
    const feedbackMessage = document.createElement('div');
    feedbackMessage.classList.add('feedback-message');

    if (isCorrect) {
        feedbackMessage.classList.add('success');
        feedbackMessage.innerHTML = '<i class="fas fa-check-circle"></i> Correct! Well done!';
        score++;
    } else {
        feedbackMessage.classList.add('error');
        feedbackMessage.innerHTML = '<i class="fas fa-times-circle"></i> Incorrect. Try again later!';
    }

    document.querySelector('.quiz-question').appendChild(feedbackMessage);

    // Add next button
    const nextButton = document.createElement('button');
    nextButton.classList.add('next-button');

    if (currentQuestionIndex === quizData.length - 1) {
        nextButton.textContent = 'See Results';
    } else {
        nextButton.textContent = 'Next Question';
    }

    nextButton.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default action
        e.stopPropagation(); // Stop event bubbling
        currentQuestionIndex++;
        displayQuizQuestion();
    });

    document.querySelector('.quiz-question').appendChild(nextButton);
}

// Show Quiz Completion Screen
function showQuizCompletion() {
    let html = `
        <div class="completion-screen">
            <div class="trophy-icon"><i class="fas fa-trophy"></i></div>
            <h2>Quiz Completed!</h2>
            <p>Great job learning about JCU!</p>
            <div class="score">Your Score: ${score}/${quizData.length}</div>
            <button class="restart-button">Play Again</button>
        </div>
    `;

    gameContent.innerHTML = html;

    document.querySelector('.restart-button').addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default action
        e.stopPropagation(); // Stop event bubbling
        startQuiz();
    });
}

// ==================== EMOJI GAME FUNCTIONALITY ====================

// Emoji Game Button Click Handler
emojiBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling

    currentGame = 'emoji';
    gameTitle.textContent = 'Emoji Guessing Game';
    contentContainer.style.display = 'flex';
    gameContent.innerHTML = '<div class="loading">Loading emoji game...</div>';

    // Fetch emoji game data
    fetch('/emoji-game')
        .then(response => response.json())
        .then(data => {
            emojiGameData = data;
            startEmojiGame();
        })
        .catch(error => {
            console.error('Error loading emoji game:', error);
            gameContent.innerHTML = '<div class="error">Failed to load emoji game. Please try again.</div>';
        });
});

// Start Emoji Game
function startEmojiGame() {
    currentQuestionIndex = 0;
    score = 0;
    displayEmojiQuestion();
}

// Display Current Emoji Question
function displayEmojiQuestion() {
    if (currentQuestionIndex >= emojiGameData.length) {
        showEmojiCompletion();
        return;
    }

    const question = emojiGameData[currentQuestionIndex];

    // Create progress dots
    let progressHTML = '<div class="progress-indicator">';
    for (let i = 0; i < emojiGameData.length; i++) {
        let dotClass = i < currentQuestionIndex ? 'completed' : (i === currentQuestionIndex ? 'active' : '');
        progressHTML += `<div class="progress-dot ${dotClass}"></div>`;
    }
    progressHTML += `</div>`;

    // Create question HTML
    let html = `
        ${progressHTML}
        <div class="emoji-question" data-index="${currentQuestionIndex}">
            <div class="emoji-display">${question.emoji}</div>
            <div class="emoji-question-text">${question.question}</div>
            <div class="emoji-answer-form">
                <input type="text" class="emoji-input" placeholder="Type your answer..." autocomplete="off">
                <button class="emoji-submit">Submit</button>
            </div>
        </div>
    `;

    gameContent.innerHTML = html;

    // Add event listener to submit button
    document.querySelector('.emoji-submit').addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default action
        e.stopPropagation(); // Stop event bubbling
        const answer = document.querySelector('.emoji-input').value.trim();
        checkEmojiAnswer(answer);
    });

    // Submit on Enter key
    document.querySelector('.emoji-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent default action
            e.stopPropagation(); // Stop event bubbling
            const answer = document.querySelector('.emoji-input').value.trim();
            checkEmojiAnswer(answer);
        }
    });

    // Focus the input field
    document.querySelector('.emoji-input').focus();
}

// Check Emoji Game Answer
function checkEmojiAnswer(answer) {
    // Prevent multiple submissions
    if (document.querySelector('.feedback-message')) return;

    const question = emojiGameData[currentQuestionIndex];

    // Check if answer is in the acceptable answers array (case insensitive)
    const isCorrect = question.answer.some(correctAnswer =>
        correctAnswer.toLowerCase() === answer.toLowerCase()
    );

    // Disable input and submit button
    document.querySelector('.emoji-input').disabled = true;
    document.querySelector('.emoji-submit').disabled = true;

    // Show feedback
    const feedbackMessage = document.createElement('div');
    feedbackMessage.classList.add('feedback-message');

    if (isCorrect) {
        feedbackMessage.classList.add('success');
        feedbackMessage.innerHTML = '<i class="fas fa-check-circle"></i> Correct! Well done!';
        score++;
    } else {
        feedbackMessage.classList.add('error');
        feedbackMessage.innerHTML = <i class="fas fa-times-circle"></i> Not quite right. Try again later!;
    }

    document.querySelector('.emoji-question').appendChild(feedbackMessage);

    // Add next button
    const nextButton = document.createElement('button');
    nextButton.classList.add('next-button');

    if (currentQuestionIndex === emojiGameData.length - 1) {
        nextButton.textContent = 'See Results';
    } else {
        nextButton.textContent = 'Next Question';
    }

    nextButton.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default action
        e.stopPropagation(); // Stop event bubbling
        currentQuestionIndex++;
        displayEmojiQuestion();
    });

    document.querySelector('.emoji-question').appendChild(nextButton);
}

// Show Emoji Game Completion Screen
function showEmojiCompletion() {
    let html = `
        <div class="completion-screen">
            <div class="trophy-icon"><i class="fas fa-trophy"></i></div>
            <h2>Emoji Game Completed!</h2>
            <p>Great emoji guessing skills!</p>
            <div class="score">Your Score: ${score}/${emojiGameData.length}</div>
            <button class="restart-button">Play Again</button>
        </div>
    `;

    gameContent.innerHTML = html;

    document.querySelector('.restart-button').addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default action
        e.stopPropagation(); // Stop event bubbling
        startEmojiGame();
    });
}

// ==================== FAQ FUNCTIONALITY ====================

// FAQ Button Click Handler
faqBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling

    currentGame = 'faq';
    gameTitle.textContent = 'Frequently Asked Questions';
    contentContainer.style.display = 'flex';
    gameContent.innerHTML = '<div class="loading">Loading FAQs...</div>';

    // Fetch FAQ data
    fetch('/faq')
        .then(response => response.json())
        .then(data => {
            faqData = data;
            displayFAQs();
        })
        .catch(error => {
            console.error('Error loading FAQs:', error);
            gameContent.innerHTML = '<div class="error">Failed to load FAQs. Please try again.</div>';
        });
});

// Display FAQs
function displayFAQs() {
    let html = '<div class="faq-container">';

    faqData.forEach((faq, index) => {
        html += `
            <div class="faq-item">
                <div class="faq-question" data-index="${index}">
                    ${faq.question}
                    <span class="faq-toggle">▼</span>
                </div>
                <div class="faq-answer">
                    ${faq.answer}
                </div>
            </div>
        `;
    });

    html += `</div>`;

    gameContent.innerHTML = html;

    // Add event listeners to FAQ questions
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', toggleFAQ);
    });
}

// Toggle FAQ Answer Visibility
function toggleFAQ(e) {
    e.preventDefault(); // Prevent default action
    e.stopPropagation(); // Stop event bubbling

    const question = e.currentTarget;
    const answer = question.nextElementSibling;

    // Toggle the active class on the question
    question.classList.toggle('active');

    // Toggle the show class on the answer
    answer.classList.toggle('show');
}

// Prevent event propagation for all click events inside game content
gameContent.addEventListener('click', function(e) {
    e.stopPropagation();
});

// Prevent input events from closing the chatbot
contentContainer.addEventListener('click', function(e) {
    e.stopPropagation();
});