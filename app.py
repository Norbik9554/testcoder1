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

# Endpoint do odbierania danych i zapisywania do Firestore
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

        # Kolejność kluczy dla "info"
        ordered_keys_info = [
            "Architecture", "CPU Processor", "Computer Name", "Cores",
            "Disks", "GPU Processor", "Hostname", "IP Address", "RAM (Gb)",
            "Release", "System", "Threads", "Type Connection"
        ]

        # Pobranie danych systemowych i uporządkowanie jako LISTA SŁOWNIKÓW
        system_info = data.get("system_info", {})
        sorted_info = [{"key": key, "value": system_info.get(key, "Brak danych")} for key in ordered_keys_info]

        # Kolejność kluczy dla "location"
        ordered_keys_location = [
            "Latitude", "Longitude", "City", "Region",
            "Country", "ISP", "ZIP Code"
        ]

        # Pobranie danych lokalizacji i uporządkowanie jako LISTA SŁOWNIKÓW
        location_info = data.get("location", {})
        sorted_location = [{"key": key, "value": location_info.get(key, "Brak danych")} for key in ordered_keys_location]

        # Finalna struktura JSON
        final_data = {
            "client_name": client_name,
            "info": sorted_info,   # INFO jako lista zachowująca kolejność
        }

        # Dodajemy lokalizację, jeśli istnieje
        if location_info:
            final_data["location"] = sorted_location  # LOCATION jako lista

        # Zapis do Firestore (nadpisując dane pod nazwą klienta)
        db.collection("users").document(client_name).set(final_data)

        return jsonify({"message": "Dane zapisane!", "id": client_name})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
