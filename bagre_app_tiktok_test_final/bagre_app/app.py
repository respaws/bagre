
from flask import Flask, render_template, request, redirect, url_for, jsonify
from tiktok_creator.create_tiktok_account import criar_conta_tiktok

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/criar_tiktok", methods=["POST"])
def criar_tiktok():
    resultado = criar_conta_tiktok()
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
