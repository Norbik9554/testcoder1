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

        # Kolejność kluczy WYMUSZONA dla "info"
        ordered_keys_info = [
            "Architecture", "CPU Processor", "Computer Name", "Cores",
            "Disks", "GPU Processor", "Hostname", "IP Address", "RAM (Gb)",
            "Release", "System", "Threads", "Type Connection"
        ]

        # Pobranie danych systemowych i ułożenie w odpowiedniej kolejności
        system_info = data.get("system_info", {})
        sorted_info = {key: system_info.get(key, "Brak danych") for key in ordered_keys_info}

        # Kolejność kluczy WYMUSZONA dla "location"
        ordered_keys_location = [
            "Latitude", "Longitude", "City", "Region",
            "Country", "ISP", "ZIP Code"
        ]

        # Pobranie danych lokalizacji i ułożenie w odpowiedniej kolejności
        location_info = data.get("location", {})
        sorted_location = {key: location_info.get(key, "Brak danych") for key in ordered_keys_location}

        # Finalna struktura JSON
        final_data = {
            "client_name": client_name,
            "info": sorted_info  # Wszystkie dane systemowe w jednej sekcji
        }

        # Dodajemy lokalizację, jeśli jest dostępna
        if location_info:
            final_data["location"] = sorted_location

        # Zapis do Firestore (nadpisując dane pod nazwą klienta)
        db.collection("users").document(client_name).set(final_data)

        return jsonify({"message": "Dane zapisane!", "id": client_name})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint testowy do wysyłania przykładowych danych
@app.route("/test", methods=["GET"])
def test():
    test_data = {
        "client_name": "Test_Client",
        "system_info": {
            "Architecture": "64bit",
            "CPU Processor": "Intel i5",
            "Computer Name": "Test-PC",
            "Cores": 4,
            "Disks": "SSD 1TB",
            "GPU Processor": "RTX 4060",
            "Hostname": "Test-Host",
            "IP Address": "192.168.1.100",
            "RAM (Gb)": "16",
            "Release": "10",
            "System": "Windows",
            "Threads": 8,
            "Type Connection": "WiFi"
        },
        "location": {
            "Latitude": 54.4197,
            "Longitude": 18.5763,
            "City": "Gdansk",
            "Region": "Pomerania",
            "Country": "Poland",
            "ISP": "Technica",
            "ZIP Code": "80-333"
        }
    }
    
    db.collection("users").document(test_data["client_name"]).set(test_data)
    return jsonify({"message": "Testowe dane zapisane!", "id": test_data["client_name"]})

if __name__ == "__main__":
    app.run(debug=True)
