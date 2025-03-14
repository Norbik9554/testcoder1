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

        # Lista kluczy do uporządkowania
        ordered_keys = ["Computer Name", "Hostname", "System", "Release", "Architecture",
                        "CPU Processor", "Cores", "Threads", "GPU Processor", "RAM (Gb)", 
                        "Disks", "Type Connection", "IP Address"]

        # Tworzymy nowy słownik tylko z istniejących danych
        sorted_data = {key: data.get(key, "Brak danych") for key in ordered_keys}

        # Dodajemy resztę pól, które były w oryginalnym `data`, ale nie były w `ordered_keys`
        for key in data:
            if key not in ordered_keys:
                sorted_data[key] = data[key]

        # Zapis do Firestore (nadpisując dane pod nazwą klienta)
        db.collection("users").document(client_name).set(sorted_data)

        return jsonify({"message": "Dane zapisane!", "id": client_name})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint testowy do wysyłania przykładowych danych
@app.route("/test", methods=["GET"])
def test():
    test_data = {
        "client_name": "Test_Client",
        "Computer Name": "Test-PC",
        "Hostname": "Test-Host",
        "System": "Windows",
        "Release": "10",
        "Architecture": "x64",
        "CPU Processor": "Intel i5",
        "Cores": 4,
        "Threads": 8,
        "GPU Processor": "RTX 4060",
        "RAM (Gb)": 16,
        "Disks": "SSD 1TB",
        "Type Connection": "WiFi",
        "IP Address": "192.168.1.100",
        "Custom Field": "Extra data"
    }
    
    response = db.collection("users").document(test_data["client_name"]).set(test_data)
    return jsonify({"message": "Testowe dane zapisane!", "id": test_data["client_name"]})

if __name__ == "__main__":
    app.run(debug=True)
