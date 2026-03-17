import argparse
import os
import secrets
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.environ.get("APP_NAME", "bagre_app")
ADMIN_USER = os.environ.get("ADMIN_USER", "bagre")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "91980514xx")
AUTOMATION_KEY = os.environ.get("AUTOMATION_KEY", "")
EXTRA_USERS = os.environ.get("EXTRA_USERS", "")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-" + APP_NAME)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            kind TEXT,
            video_id TEXT,
            seconds INTEGER,
            comment TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    return conn


def ensure_default_users():
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(username, password) VALUES(?, ?)",
            (ADMIN_USER, ADMIN_PASS),
        )
        for raw in EXTRA_USERS.split(","):
            raw = raw.strip()
            if not raw or ":" not in raw:
                continue
            username, password = raw.split(":", 1)
            conn.execute(
                "INSERT OR IGNORE INTO users(username, password) VALUES(?, ?)",
                (username.strip(), password.strip()),
            )


def get_user(username):
    conn = get_db()
    row = conn.execute(
        "SELECT username, password FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return row


def require_automation_key():
    if not AUTOMATION_KEY:
        return jsonify({"error": "automation_disabled"}), 403
    sent_key = request.headers.get("X-Automation-Key", "")
    if sent_key != AUTOMATION_KEY:
        return jsonify({"error": "invalid_automation_key"}), 403
    return None


@app.route("/")
def index():
    if not session.get("user"):
        return render_template("login.html")
    return render_template("dashboard.html", user=session["user"], app_name=APP_NAME)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    row = get_user(username)
    if row and row[1] == password:
        session["user"] = username
        return redirect("/")
    return "Credenciais inválidas", 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def save_event(kind, payload, user=None):
    event_user = user or session.get("user")
    if not event_user:
        return jsonify({"error": "unauth"}), 401

    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO events(user, kind, video_id, seconds, comment) VALUES(?,?,?,?,?)",
            (
                event_user,
                kind,
                payload.get("video_id"),
                payload.get("seconds"),
                payload.get("comment"),
            ),
        )
    return jsonify({"ok": True})


@app.route("/api/watch", methods=["POST"])
def api_watch():
    return save_event("watch", request.json or {})


@app.route("/api/like", methods=["POST"])
def api_like():
    return save_event("like", request.json or {})


@app.route("/api/comment", methods=["POST"])
def api_comment():
    return save_event("comment", request.json or {})


@app.route("/api/automation/create-users", methods=["POST"])
def api_create_users():
    key_error = require_automation_key()
    if key_error:
        return key_error

    payload = request.json or {}
    count = min(max(int(payload.get("count", 1)), 1), 5000)
    prefix = payload.get("prefix", "auto_user")
    default_password = payload.get("password", "123456")

    created = []
    conn = get_db()
    with conn:
        for _ in range(count):
            username = f"{prefix}_{secrets.token_hex(4)}"
            conn.execute(
                "INSERT OR IGNORE INTO users(username, password) VALUES(?, ?)",
                (username, default_password),
            )
            created.append(username)

    return jsonify({"ok": True, "created": len(created), "users": created})


@app.route("/api/automation/generate-views", methods=["POST"])
def api_generate_views():
    key_error = require_automation_key()
    if key_error:
        return key_error

    payload = request.json or {}
    users = payload.get("users", [])
    video_id = payload.get("video_id", "video_auto")
    per_user = min(max(int(payload.get("views_per_user", 1)), 1), 200)

    if not users:
        return jsonify({"error": "users_required"}), 400

    total = 0
    for username in users:
        if get_user(username):
            for _ in range(per_user):
                save_event(
                    "watch",
                    {"video_id": video_id, "seconds": int(payload.get("seconds", 8))},
                    user=username,
                )
                total += 1

    return jsonify({"ok": True, "views_recorded": total, "video_id": video_id})


@app.route("/admin/events")
def admin_events():
    if not session.get("user"):
        return "unauthorized", 401
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id,user,kind,video_id,seconds,comment,ts FROM events ORDER BY id DESC LIMIT 500"
    ).fetchall()
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, row)) for row in rows]
    return jsonify(data)


ensure_default_users()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=False)
