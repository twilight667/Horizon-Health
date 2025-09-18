# chatbot_larger_text.py
import sys, json, random, re, string, html
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QSplitter, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HealthChat - Readable UI")
        self.setMinimumSize(1000, 650)
        self.load_resources()
        self.setup_ui()
        self.showMaximized()

    def load_resources(self):
        with open("contagious_diseases_dataset.json", "r", encoding="utf-8") as f:
            self.diseases_data = json.load(f)
        self.disease_index = {d["disease"].lower(): d for d in self.diseases_data}
        self.ALIASES = {
            "flu": "influenza (flu)",
            "corona": "covid-19",
            "chickenpox": "varicella"
        }
        with open("intents.json", "r", encoding="utf-8") as f:
            self.intents = json.load(f)
        self.intent_classifier = IntentClassifier(self.intents)

    def setup_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left = QWidget()
        lyt_left = QVBoxLayout(left)
        lyt_left.setContentsMargins(15, 15, 15, 15)
        lyt_left.setSpacing(12)

        # Header
        header = QLabel("<b>HealthChat</b>")
        header.setFont(QFont("Arial", 26))  # Heading larger
        lyt_left.addWidget(header)

        # Mode selection
        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Light", "Dark"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        lyt_left.addLayout(mode_row)

        # Messages
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setAcceptRichText(True)
        self.messages.setFont(QFont("Arial", 22))  # Chat messages slightly smaller than header
        self.messages.setStyleSheet("background:transparent; border:none;")
        lyt_left.addWidget(self.messages, 1)

        # Input row
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your message or symptoms...")
        self.input.setFont(QFont("Arial", 20))
        self.input.returnPressed.connect(self.on_send)
        send_btn = QPushButton("Send")
        send_btn.setFont(QFont("Arial", 20))
        send_btn.clicked.connect(self.on_send)
        send_btn.setFixedWidth(140)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(send_btn)
        lyt_left.addLayout(input_row)

        # Right panel: tips + export
        right = QWidget()
        lyt_right = QVBoxLayout(right)
        lyt_right.setContentsMargins(15,15,15,15)
        lyt_right.setSpacing(12)
        tips_label = QLabel("<b>Healthy Tips</b>")
        tips_label.setFont(QFont("Arial", 22))
        lyt_right.addWidget(tips_label)
        self.tips_text = QTextEdit()
        self.tips_text.setReadOnly(True)
        self.tips_text.setFont(QFont("Arial", 20))
        self.tips_text.setPlainText(
            "• Stay hydrated.\n• Keep a symptom diary.\n• If symptoms persist, consult a professional."
        )
        lyt_right.addWidget(self.tips_text, 1)
        export_btn = QPushButton("Export chat")
        export_btn.setFont(QFont("Arial", 20))
        export_btn.clicked.connect(self.export_chat)
        lyt_right.addWidget(export_btn)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([750, 350])
        self.setCentralWidget(splitter)

        # Default mode
        self.change_mode("Light")

    def change_mode(self, mode):
        if mode == "Light":
            bg_color = "#f9f9f9"
            user_bg = "#d0f0c0"
            bot_bg = "#f0f0f0"
            text_color = "#000000"
            sidebar_bg = "#e8e8e8"
            self.setStyleSheet(f"QWidget {{ background-color: {bg_color}; color: {text_color}; }}")
            self.user_bg = user_bg
            self.bot_bg = bot_bg
            self.tips_text.setStyleSheet(f"background-color: {sidebar_bg}; color: {text_color};")
        else:
            bg_color = "#1e1e1e"
            user_bg = "#43cea2"
            bot_bg = "#2d2d2d"
            text_color = "#e8e8e8"
            sidebar_bg = "#000000"
            self.setStyleSheet(f"QWidget {{ background-color: {bg_color}; color: {text_color}; }}")
            self.user_bg = user_bg
            self.bot_bg = bot_bg
            self.tips_text.setStyleSheet(f"background-color: {sidebar_bg}; color: {text_color};")

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
        except Exception as e:
            print("Failed to export:", e)

    def add_message(self, role, text):
        font_size = 28
        padding = 12
        line_height = 1.6
        max_width = 75

        if role == "user":
            block = f'''
            <div style="text-align:right; margin:6px">
                <span style="background:{self.user_bg}; padding:{padding}px; border-radius:12px;
                            display:inline-block; max-width:{max_width}%; font-size:{font_size}px;
                            line-height:{line_height}; vertical-align:top; text-align:right;">
                {text}</span>
            </div>'''
        else:
            block = f'''
            <div style="text-align:left; margin:6px">
                <span style="background:{self.bot_bg}; padding:{padding}px; border-radius:12px;
                            display:inline-block; max-width:{max_width}%; font-size:{font_size}px;
                            line-height:{line_height}; vertical-align:top; text-align:left;">
                {text}</span>
            </div>'''

        self.messages.insertHtml(block)
        self.messages.verticalScrollBar().setValue(self.messages.verticalScrollBar().maximum())



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

    def generate_reply(self, user_text):
        user_input_lower = user_text.lower()
        disease_info = None
        # Check aliases first
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
        # Infer disease from symptoms if no direct match
        if not disease_info:
            disease_info = self.infer_disease_from_symptoms(user_text)

        if disease_info:
            name = disease_info["disease"]
            symptoms = disease_info.get("symptoms", [])
            precautions = disease_info.get("precautions", [])
            actions = disease_info.get("actions", [])

            # Build HTML safely
            symptoms_html = "".join(f"<li>{html.escape(s)}</li>" for s in symptoms)
            precautions_html = "".join(f"<li>{html.escape(p)}</li>" for p in precautions)
            actions_html = "".join(f"<li>{html.escape(a)}</li>" for a in actions)

            reply = f"""
            <b>Disease Name:</b> {html.escape(name)}<br><br>

            <b>Symptoms:</b>
            <ul>
                {symptoms_html}
            </ul>

            <b>Precautions:</b>
            <ul>
                {precautions_html}
            </ul>

            <b>Recommended Actions:</b>
            <ul>
                {actions_html}
            </ul>
            """
            return reply

        # If no disease info, fallback to intents
        intent_tag = self.intent_classifier.predict_intent(user_text)
        for intent in self.intents.get("intents", []):
            if intent["tag"] == intent_tag:
                return random.choice(intent.get("responses", ["Sorry, I couldn't understand."]))
        return "Sorry, I couldn't understand. Please provide more details or symptoms."


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
