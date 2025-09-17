# 🩺 Health Guidance Chatbot  

A simple NLP-powered chatbot that provides **symptoms, precautions, and actions** for common diseases using fixed CDC/WHO data. The bot understands natural language queries, greetings, and even **mixed prompts** like *“hi, can you tell me the symptoms of malaria?”*.  

---

## 📌 Features  
- **Fixed Knowledge Base**: Uses curated JSON dataset for diseases.  
- **Intent Recognition**: Detects whether the user asks about **symptoms, precautions, or actions**.  
- **Synonym & Phrase Coverage**: Handles many ways of asking the same thing.  
- **Greeting + Question Handling**: Can parse mixed prompts (e.g., *“hello, how do I prevent flu?”*).  
- **Fallback Responses**: If unsure, politely asks for clarification.  

---

## 📂 Project Structure  

```
health-chatbot/
│
├── data/
│   └── intents.json      # Intent definitions (patterns + tags)
│
├── chatbot.py            # Main chatbot logic
├── nlp_utils.py          # Preprocessing + intent detection
│
├── README.md             # Project documentation
```

---

## ⚙️ How It Works  

1. **User Input → Preprocessing**  
   - Converts text to lowercase, removes extra punctuation.  

2. **Intent Detection**  
   - Matches input against patterns from `intents.json`.  
   - Uses regex with wildcard `*` for disease names.  
   - Prioritizes disease-related intents over greetings.  

3. **Response Generation**  
   - Fetches correct info (symptoms / precautions / actions).  
   - Wraps response in conversational template (e.g., *“Hi there! Here are the symptoms of malaria…”*).  

---

## 📑 Intents File (`intents.json`)  

Each intent contains:  
- `tag`: intent name (`symptoms`, `precautions`, `actions`, `greeting`, `goodbye`, `fallback`)  
- `patterns`: list of possible user queries  

Example:  
```json
{
  "tag": "symptoms",
  "patterns": [
    "what are the symptoms of *",
    "how do I know if I have *",
    "hi, can you tell me the symptoms of *"
  ]
}
```

---

## ▶️ Running the Bot  

1. Clone the repository:  
   ```bash
   git clone git@github.com:twilight667/Horizon-Health.git
   ```

2. Run the app:  
   ```bash
   python app.py
   ```

3. Example interaction:  
   ```
   User: hi, what are the symptoms of covid-19?
   Bot: Hello! The common symptoms of COVID-19 include fever, cough, tiredness, and loss of taste or smell.
   ```

---

## 📌 Future Upgrades  
- Add **response templates** for more natural replies.  
- Integrate **sentence embeddings** (e.g., Sentence-BERT) for semantic intent recognition.  
- Provide more insights on diseases
- Use a more secure data structure and improve searching method

---

## ⚠️ Disclaimer  
This chatbot is for **educational purposes only**.  
It is **not a replacement for medical professionals**.  
Always consult a doctor for real health concerns.  
