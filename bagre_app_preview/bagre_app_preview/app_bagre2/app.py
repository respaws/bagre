import os, sqlite3, argparse
from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.environ.get("APP_NAME", "bagre_app")
ADMIN_USER = os.environ.get("ADMIN_USER", "bagre")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "91980514xx")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-" + APP_NAME)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            kind TEXT,
            video_id TEXT,
            seconds INTEGER,
            comment TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    return conn

@app.route('/')
def index():
    if not session.get('user'):
        return render_template('login.html')
    return render_template('dashboard.html', user=session['user'], app_name=APP_NAME)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username', '')
    p = request.form.get('password', '')
    if u == ADMIN_USER and p == ADMIN_PASS:
        session['user'] = u
        return redirect('/')
    return "Credenciais inválidas", 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def save_event(kind, payload):
    if not session.get('user'):
        return jsonify({'error':'unauth'}), 401
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO events(user, kind, video_id, seconds, comment) VALUES(?,?,?,?,?)",
            (session['user'], kind, payload.get('video_id'), payload.get('seconds'), payload.get('comment'))
        )
    return jsonify({'ok': True})

@app.route('/api/watch', methods=['POST'])
def api_watch():
    return save_event('watch', request.json or {})

@app.route('/api/like', methods=['POST'])
def api_like():
    return save_event('like', request.json or {})

@app.route('/api/comment', methods=['POST'])
def api_comment():
    return save_event('comment', request.json or {})

@app.route('/admin/events')
def admin_events():
    # simples listagem em JSON
    if not session.get('user'):
        return "unauthorized", 401
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("SELECT id,user,kind,video_id,seconds,comment,ts FROM events ORDER BY id DESC LIMIT 500").fetchall()
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, r)) for r in rows]
    return jsonify(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)))
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=False)
