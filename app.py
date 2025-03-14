import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify

app = Flask(__name__)

# Pobranie JSON-a z Render Environment Variables
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# Inicjalizacja Firestore
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Serwer działa poprawnie!"})

# Endpoint do odbierania danych od użytkownika i zapisywania do Firestore
@app.route("/save", methods=["POST"])
def save_data():
    try:
        data = request.json  # Pobranie danych od użytkownika
        if not data:
            return jsonify({"error": "Brak danych"}), 400

        # Zapis do Firestore (kolekcja "users")
        doc_ref = db.collection("users").add(data)
        return jsonify({"message": "Dane zapisane!", "id": doc_ref[1].id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
