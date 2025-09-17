import json
import re
import string

# Load diseases dataset
def load_diseases(path="contagious_diseases_dataset.json"):
    with open(path, "r") as f:
        data = json.load(f)
    # create index for fast lookup using lowercase
    disease_index = {d["disease"].lower(): d for d in data}
    return data, disease_index

# Load intents
def load_intents(path="intents.json"):
    with open(path, "r") as f:
        return json.load(f)

# Intent classifier using regex wildcard patterns
class IntentClassifier:
    def __init__(self, intents):
        self.intents = intents["intents"]

    def predict_intent(self, user_input):
        # clean input
        clean_input = user_input.lower().translate(str.maketrans("", "", string.punctuation))
        for intent in self.intents:
            for pattern in intent["patterns"]:
                regex_pattern = pattern.replace("*", "(.*)")
                if re.search(regex_pattern, clean_input, re.IGNORECASE):
                    return intent["tag"]
        return "fallback"

# Disease finder with dictionary + aliases
ALIASES = {
    "flu": "influenza",
    "corona": "covid-19",
    "chickenpox": "varicella"
}

def find_disease_info(user_input, disease_index):
    user_input_lower = user_input.lower()
    # check aliases first
    for alias, actual in ALIASES.items():
        if alias in user_input_lower:
            return disease_index.get(actual)
    # check exact names
    for name in disease_index:
        if name in user_input_lower:
            return disease_index[name]
    return None
