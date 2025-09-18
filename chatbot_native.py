# chatbot_full.py
import sys, json, random, re, string, html
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QSplitter, QFileDialog
)
from PyQt5.QtCore import Qt

# ----------------- Intent Classifier -----------------
class IntentClassifier:
    def __init__(self, intents):
        self.intents = intents["intents"]

    def predict_intent(self, user_input):
        clean_input = user_input.lower().translate(str.maketrans("", "", string.punctuation))
        for intent in self.intents:
            for pattern in intent.get("patterns", []):
                regex_pattern = pattern.replace("*", "(.*)")
                if re.search(regex_pattern, clean_input, re.IGNORECASE):
                    return intent["tag"]
        return "fallback"

# ----------------- Main Window -----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HealthChat - Native Desktop")
        self.setMinimumSize(900, 600)

        # Load resources
        self.load_resources()

        # Splitter: left = chat, right = tips
        splitter = QSplitter(Qt.Horizontal)
        left = QWidget(); lyt_left = QVBoxLayout(left); lyt_left.setContentsMargins(12,12,12,12)
        right = QWidget(); lyt_right = QVBoxLayout(right); lyt_right.setContentsMargins(12,12,12,12)

        # Header
        header = QLabel("<b>HealthChat</b> — Native UI")
        header.setFixedHeight(36)
        lyt_left.addWidget(header)

        # Messages area
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setAcceptRichText(True)
        lyt_left.addWidget(self.messages, 1)

        # Input + send
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your message or symptoms...")
        self.input.returnPressed.connect(self.on_send)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.on_send)
        row.addWidget(self.input, 1); row.addWidget(send_btn)
        lyt_left.addLayout(row)

        # Right sidebar: tips + export
        tips_label = QLabel("<b>Healthy Tips</b>")
        lyt_right.addWidget(tips_label)
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setPlainText(
            "• Stay hydrated.\n• Keep a symptom diary.\n• If symptoms persist, consult a professional."
        )
        lyt_right.addWidget(tips_text, 1)
        export_btn = QPushButton("Export chat")
        export_btn.clicked.connect(self.export_chat)
        lyt_right.addWidget(export_btn)

        splitter.addWidget(left); splitter.addWidget(right)
        splitter.setSizes([700, 300])
        self.setCentralWidget(splitter)

    # ----------------- Load resources -----------------
    def load_resources(self):
        # Load disease dataset
        with open("contagious_diseases_dataset.json", "r", encoding="utf-8") as f:
            self.diseases_data = json.load(f)
        self.disease_index = {d["disease"].lower(): d for d in self.diseases_data}
        self.ALIASES = {
            "flu": "influenza (flu)",
            "corona": "covid-19",
            "chickenpox": "varicella"
        }

        # Load intents
        with open("intents.json", "r", encoding="utf-8") as f:
            self.intents = json.load(f)
        self.intent_classifier = IntentClassifier(self.intents)

    # ----------------- Button handlers -----------------
    def on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.add_message("user", text)
        self.input.clear()
        reply = self.generate_reply(text)
        self.add_message("bot", reply)

    def export_chat(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save chat", "chat_export.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.messages.toPlainText())
            print("Exported chat to", path)
        except Exception as e:
            print("Failed to export:", e)

    # ----------------- UI helper -----------------
    def add_message(self, role, text):
        safe = html.escape(text)
        if role == "user":
            block = f'<div style="text-align:right;margin:6px"><span style="background:#bdecd6;color:#012018;padding:8px;border-radius:10px;display:inline-block;max-width:78%">{safe}</span></div>'
        else:
            block = f'<div style="text-align:left;margin:6px"><span style="background:#0f1724;color:#e6eef6;padding:8px;border-radius:10px;display:inline-block;max-width:78%">{safe}</span></div>'
        self.messages.append(block)

    # ----------------- Disease inference -----------------
    def infer_disease_from_symptoms(self, user_input):
        clean_input = user_input.lower().translate(str.maketrans("", "", string.punctuation))
        user_symptoms = set(map(str.strip, re.split(r",|and", clean_input)))

        best_match = None
        max_overlap = 0
        for disease in self.diseases_data:
            disease_symptoms = set(s.lower() for s in disease.get("symptoms", []))
            overlap = len(user_symptoms & disease_symptoms)
            if overlap > max_overlap and overlap >= 1:
                max_overlap = overlap
                best_match = disease
        return best_match

    # ----------------- Generate reply -----------------
    def generate_reply(self, user_text):
        user_input_lower = user_text.lower()
        disease_info = None

        # Check aliases
        for alias, actual in self.ALIASES.items():
            if alias in user_input_lower:
                disease_info = self.disease_index.get(actual)
                break

        # Check exact disease names
        if not disease_info:
            for name in self.disease_index:
                if name in user_input_lower:
                    disease_info = self.disease_index[name]
                    break

        # Check symptoms if no disease name found
        if not disease_info:
            disease_info = self.infer_disease_from_symptoms(user_text)

        # Construct response
        if disease_info:
            name = disease_info["disease"]
            symptoms = ", ".join(disease_info.get("symptoms", []))
            precautions = "\n".join(f"• {p}" for p in disease_info.get("precautions", []))
            actions = "\n".join(f"• {a}" for a in disease_info.get("actions", []))
            reply = (f"Based on your input, you may have **{name}**.\n\n"
                     f"**Symptoms:** {symptoms}\n\n"
                     f"**Precautions:**\n{precautions}\n\n"
                     f"**Recommended Actions:**\n{actions}")
            return reply

        # Fallback to intents
        intent_tag = self.intent_classifier.predict_intent(user_text)
        for intent in self.intents.get("intents", []):
            if intent["tag"] == intent_tag:
                return random.choice(intent.get("responses", ["Sorry, I couldn't understand."]))

        # Final fallback
        return "Sorry, I couldn't understand. Please provide more details or symptoms."

# ----------------- Run App -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
