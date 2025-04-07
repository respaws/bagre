
from flask import Flask, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)
DB_PATH = "db.json"

if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({"accounts": []}, f)

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/watch_video")
def watch_video():
    return "✅ Vídeo assistido por 3 segundos"

@app.route("/generate_comment")
def generate_comment():
    return "💬 Comentário gerado com base nos outros"

@app.route("/rotate_ip")
def rotate_ip():
    return "🔄 IP rotacionado (simulado)"

@app.route("/create_account")
def create_account():
    with open(DB_PATH, "r+") as f:
        data = json.load(f)
        new_account = {
            "username": f"user{len(data['accounts'])+1}",
            "email": f"user{len(data['accounts'])+1}@fake.com"
        }
        data["accounts"].append(new_account)
        f.seek(0)
        json.dump(data, f, indent=2)
        return f"🆕 Conta criada: {new_account}"

@app.route("/get_accounts")
def get_accounts():
    with open(DB_PATH) as f:
        return jsonify(json.load(f)["accounts"])

if __name__ == "__main__":
    app.run(debug=True)
