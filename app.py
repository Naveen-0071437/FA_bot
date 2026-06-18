from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ==== INSERT YOUR API KEY HERE ====
GEMINI_API_KEY = " "
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# ==== Default predefined fields ====
fields = {
    "Emotional": "You are a calm, caring, mostly funny, and supportive chatbot. Always reply warmly and empathetically.",
    "Trading": "You are a professional financial analyst. Provide trading insights clearly but avoid giving direct financial advice.",
    "Medical": "You are a knowledgeable medical assistant. Explain health topics clearly, but never give diagnoses or prescriptions.",
    "CS": "You are a friendly computer science mentor who explains programming concepts simply and clearly.",
    "Farming": "You are an experienced agricultural advisor who helps farmers with crop and soil advice in simple language."
}

@app.route("/fields", methods=["GET"])
def get_fields():
    """Return available field names."""
    return jsonify(list(fields.keys()))

@app.route("/fields", methods=["POST"])
def add_field():
    """Add a new custom field."""
    data = request.get_json()
    name = data.get("name")
    instructions = data.get("instructions")
    if not name or not instructions:
        return jsonify({"error": "Missing field name or instructions"}), 400
    fields[name] = instructions
    return jsonify({"message": f"Field '{name}' added successfully!"})

@app.route("/set_field", methods=["POST"])
def set_field():
    """Confirm active field."""
    data = request.get_json()
    name = data.get("name")
    if name not in fields:
        return jsonify({"error": "Unknown field"}), 400
    return jsonify({"message": f"Active field set to '{name}'", "instructions": fields[name]})

@app.route("/chat", methods=["POST"])
def chat():
    """Send chat message to Gemini API with selected field personality."""
    data = request.get_json()
    field = data.get("field", "General")
    user_message = data.get("message", "")
    prefix = fields.get(field, "You are a helpful general assistant.")

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prefix}]},
            {"role": "user", "parts": [{"text": user_message}]}
        ]
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        res_json = response.json()
        reply = (
            res_json.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "💜 Sorry, I couldn’t generate a response.")
        )
        return jsonify({"response": reply})

    except Exception as e:
        print("Error contacting Gemini API:", e)
        return jsonify({"response": "⚠️ Error contacting Gemini API."}), 500


if __name__ == "__main__":
    app.run(debug=True)
