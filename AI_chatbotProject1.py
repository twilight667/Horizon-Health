from NLP import load_diseases, load_intents, IntentClassifier, find_disease_info

# Load data
DISEASES_LIST, DISEASES_INDEX = load_diseases("contagious_diseases_dataset.json")
INTENTS = load_intents("intents.json")
classifier = IntentClassifier(INTENTS)

print("🤖 Horizon Health Chatbot (type 'quit' to exit)")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        print("🤖 Goodbye! Stay safe! 🩺")
        break

    intent = classifier.predict_intent(user_input)
    disease_info = find_disease_info(user_input, DISEASES_INDEX)

    if intent == "greeting":
        print("🤖 Hello! Ask me about any disease, its symptoms, precautions, or actions.")
    elif intent == "goodbye":
        print("🤖 Take care! 👋")
        break
    elif disease_info:
        if intent == "symptoms":
            print(f"ℹ️ Symptoms of {disease_info['disease']}: {', '.join(disease_info.get('symptoms', []))}")
        elif intent == "precautions":
            print(f"🛡️ Precautions for {disease_info['disease']}: {', '.join(disease_info.get('precautions', []))}")
        elif intent == "actions":
            print(f"⚡ Actions for {disease_info['disease']}: {', '.join(disease_info.get('actions', []))}")
        else:
            print(f"ℹ️ I found information about {disease_info['disease']}. You can ask about symptoms, precautions, or actions.")
    else:
        print("❌ Sorry, I couldn’t detect any disease. Try again with a clear question.")
