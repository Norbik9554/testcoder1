from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
import couchdb
import os

app = Flask(__name__)
CORS(app)  # Pozwala na dostęp do API z innych urządzeń
auth = HTTPTokenAuth(scheme="Bearer")

# 🔑 Klucz uwierzytelniający (zmień na swój!)
ACCESS_TOKENS = {"slave_token": "123456", "master_token": "abcdef"}

# 🔗 Dane dostępowe do CouchDB
COUCHDB_URL = os.getenv("COUCHDB_URL", "http://admin:password@localhost:5984/")
COUCHDB_DB = "sensor_data"

# 🔧 Połączenie z bazą
couch = couchdb.Server(COUCHDB_URL)
if COUCHDB_DB not in couch:
    db = couch.create(COUCHDB_DB)
else:
    db = couch[COUCHDB_DB]

@auth.verify_token
def verify_token(token):
    return token in ACCESS_TOKENS.values()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Serwer działa poprawnie!"})

@app.route("/data", methods=["POST"])
@auth.login_required
def receive_data():
    """Slave przesyła dane do serwera"""
    data = request.json
    if not data:
        return jsonify({"error": "Brak danych"}), 400
    
    doc_id, doc_rev = db.save(data)
    return jsonify({"message": "Dane zapisane", "id": doc_id}), 201

@app.route("/data", methods=["GET"])
@auth.login_required
def get_data():
    """Master pobiera dane z serwera"""
    data = [{"id": doc["_id"], **doc} for doc in db.view("_all_docs", include_docs=True)]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
