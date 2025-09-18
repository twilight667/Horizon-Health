from flask import Flask, request, jsonify, render_template
from NLP import load_diseases, load_intents, IntentClassifier, find_disease_info

# Initialize Flask
app = Flask(__name__, template_folder=".")

# Load datasets
DISEASES_LIST, DISEASES_INDEX = load_diseases("contagious_diseases_dataset.json")
INTENTS = load_intents("intents.json")
classifier = IntentClassifier(INTENTS)


@app.route("/")
def home():
    return render_template("health_bot.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"response": "⚠️ Please enter a message."})

    # Detect intent + disease
    intent = classifier.predict_intent(user_input)
    disease_info = find_disease_info(user_input, DISEASES_INDEX)

    # Build response
    if intent == "greeting":
        response = "👋 Hello! Ask me about any disease, its symptoms, precautions, or actions."
    elif intent == "goodbye":
        response = "👋 Goodbye! Stay safe and healthy!"
    elif disease_info:
        if intent == "symptoms":
            response = f"ℹ️ Symptoms of {disease_info['disease']}: {', '.join(disease_info.get('symptoms', []))}"
        elif intent == "precautions":
            response = f"🛡️ Precautions for {disease_info['disease']}: {', '.join(disease_info.get('precautions', []))}"
        elif intent == "actions":
            response = f"⚡ Actions for {disease_info['disease']}: {', '.join(disease_info.get('actions', []))}"
        else:
            response = f"ℹ️ I found information about {disease_info['disease']}. You can ask about symptoms, precautions, or actions."
    else:
        response = "❌ Sorry, I couldn’t detect any disease. Try again with a clear question."

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
