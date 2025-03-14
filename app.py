import os
import json
import firebase_admin
import traceback
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Pobranie JSON-a z Render Environment Variables
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# Inicjalizacja Firestore
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/", methods=["GET"])
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        error_message = f"Błąd renderowania strony: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

@app.route("/dodaj", methods=["POST"])
def dodaj():
    try:
        data = request.json  # Pobranie danych z żądania
        if not data:
            return jsonify({"error": "Brak danych"}), 400
        
        client_name = data.get("client_name")
        if not client_name:
            return jsonify({"error": "Brak nazwy klienta"}), 400
        
        print("Otrzymano dane od:", client_name)

        # Pobranie danych systemowych i lokalizacji bez narzucania kolejności
        system_info = data.get("system_info", {})
        location_info = data.get("location", {})

        # Finalna struktura JSON
        final_data = {
            "client_name": client_name,
            "info": system_info,   # INFO jako oryginalny słownik
            "location": location_info if location_info else None,  # Jeśli brak danych, zostaw None
        }

        # Zapis do Firestore (nadpisując dane pod nazwą klienta)
        db.collection("users").document(client_name).set(final_data)

        return jsonify({"message": "Dane zapisane!", "id": client_name})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
