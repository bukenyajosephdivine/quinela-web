import json
import re
from datetime import datetime

# ---------- JSON UTILITIES ----------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------- TEXT UTILITIES ----------
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()

def similarity(q1, q2):
    s1 = set(q1.split())
    s2 = set(q2.split())
    if not s1 or not s2:
        return 0
    return len(s1 & s2) / len(s1 | s2)

# ---------- LOAD MEMORY ----------
identity = load_json("identity.json")
knowledge = load_json("memory/knowledge.json")

THRESHOLD = 0.6

# ---------- RESPONSE FUNCTION ----------
def get_response(user_input):
    normalized_input = normalize(user_input)
    best_match = None
    best_score = 0

    for qa in knowledge.get("qa_pairs", []):
        stored = normalize(qa["question"])
        score = similarity(normalized_input, stored)

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score >= THRESHOLD:
        best_match["confidence"] = best_match.get("confidence", 1) + 1
        best_match["last_used"] = datetime.now().isoformat()
        save_json("memory/knowledge.json", knowledge)

        return best_match["answer"], False

    return "I don't know this yet. Can you teach me?", True

# ---------- LEARNING FUNCTION ----------
def learn(question, answer):
    knowledge.setdefault("qa_pairs", []).append({
        "question": question,
        "answer": answer,
        "confidence": 1,
        "learned_on": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    })

    save_json("memory/knowledge.json", knowledge)