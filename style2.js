const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const voiceBtn = document.getElementById('voiceBtn');
let recognition = null;

const initialMessages = [
    "Namaste! Welcome to Ayurveda HealthAI.",
    "How can I help you today?",
];

function addMessage(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${type}-message`);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendMessage() {
    const inputMessage = userInput.value.trim();
    if (inputMessage) {
        addMessage(inputMessage, 'user');
        userInput.value = '';

        // Call backend API
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: inputMessage })
        })
        .then(response => response.json())
        .then(data => {
            // Show remedy and yoga from the response
            if (data.remedy && data.yoga) {
                addMessage(`Remedy: ${data.remedy}`, 'ai');
                addMessage(`Yoga: ${data.yoga}`, 'ai');
            } else {
                addMessage(data.message, 'ai');
            }
        })
        .catch(error => {
            addMessage("Sorry, I couldn't process that. Please try again.", 'ai');
        });
    }
}

function toggleVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Speech recognition not supported');
        return;
    }

    if (!recognition) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            voiceBtn.classList.add('listening');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage();
        };

        recognition.onend = () => {
            voiceBtn.classList.remove('listening');
            recognition = null;
        };

        recognition.start();
    } else {
        recognition.stop();
    }
}

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

initialMessages.forEach(msg => addMessage(msg, 'ai'));
