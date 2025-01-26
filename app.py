from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

# Load intents.json
with open("intents.json", "r") as file:
    intents_data = json.load(file)

# Azure AI Configuration
AZURE_KEY = "2W8YR7ksDQfdy6DkzPnakmFj6p96uQfbLhXjsD46lRcMasemXTpsJQQJ99BAACGhslBXJ3w3AAAaACOGYQp3"
AZURE_ENDPOINT = "https://aiforhealth.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=AiHealth&api-version=2021-10-01&deploymentName=production"

# Function to get predictions from Azure Knowledge Base
def get_prediction(user_input):
    """
    Call Azure Knowledge Base prediction endpoint.
    Extract relevant responses based on the user's input.
    """
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "question": user_input,
        "top": 1  # Get the most relevant response
    }
    response = requests.post(AZURE_ENDPOINT, headers=headers, json=payload)

    if response.status_code == 200:
        # Extract the answer from the response
        return response.json().get("answers", [{}])[0].get("answer", "No response found.")
    else:
        print(f"Azure Error: {response.status_code} - {response.text}")
        return "Azure service is unavailable at the moment. Please try again later."

@app.route('/')
def home():
    """Render the main chatbot page."""
    return render_template('healthcare-ai-chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle the chat input from the user.
    Retrieve a response using the Azure service or fallback intents.
    """
    user_input = request.json.get("input", "").strip()

    # Get prediction from Azure
    prediction = get_prediction(user_input)

    # Fallback to local intents.json if Azure doesn't have a proper answer
    if prediction == "No response found.":
        responses = get_response_from_intents(user_input, [])
        if responses:
            return jsonify({"remedy": responses[0], "yoga": responses[1] if len(responses) > 1 else "No yoga recommendation."})

    return jsonify({"message": prediction})

# Function to match user input with intents
def get_response_from_intents(user_input, key_phrases):
    """
    Search the intents.json data for a matching response.
    """
    for intent in intents_data["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input.lower() or any(phrase.lower() in pattern.lower() for phrase in key_phrases):
                return intent["responses"]
    return None

if __name__ == '__main__':
    app.run(debug=True)
