from NLP import load_diseases, load_intents, IntentClassifier, find_disease_info

# Load data once
DISEASES_LIST, DISEASES_INDEX = load_diseases("contagious_diseases_dataset.json")
INTENTS = load_intents("intents.json")
classifier = IntentClassifier(INTENTS)

def chatbot_response(user_input: str) -> str:
    """Return chatbot's response for a given user input (question)."""
    if user_input.lower() in ["quit", "exit", "bye"]:
        return "🤖 Goodbye! Stay safe! 🩺"

    intent = classifier.predict_intent(user_input)
    disease_info = find_disease_info(user_input, DISEASES_INDEX)

    if intent == "greeting":
        return "🤖 Hello! Ask me about any disease, its symptoms, precautions, or actions."
    elif intent == "goodbye":
        return "🤖 Take care! 👋"
    elif disease_info:
        if intent == "symptoms":
            return f"ℹ️ Symptoms of {disease_info['disease']}: {', '.join(disease_info.get('symptoms', []))}"
        elif intent == "precautions":
            return f"🛡️ Precautions for {disease_info['disease']}: {', '.join(disease_info.get('precautions', []))}"
        elif intent == "actions":
            return f"⚡ Actions for {disease_info['disease']}: {', '.join(disease_info.get('actions', []))}"
        else:
            return f"ℹ️ I found information about {disease_info['disease']}. You can ask about symptoms, precautions, or actions."
    else:
        return "❌ Sorry, I couldn’t detect any disease. Try again with a clear question."
