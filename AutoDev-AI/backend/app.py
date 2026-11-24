import os
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, create_report, list_reports, get_report, update_report
from ai_engine import analyze_report

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-this")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

init_db()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Não autorizado"}), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.get("/")
def home():
    return redirect(url_for("login"))

@app.get("/widget/<path:filename>")
def widget_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "widget"), filename)

@app.get("/dashboard")
@admin_required
def dashboard():
    return send_from_directory(os.path.join(BASE_DIR, "frontend"), "dashboard.html")

@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "frontend"), filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        expected = os.getenv("ADMIN_PASSWORD", "")
        if expected and password == expected:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        return """<p>Senha incorreta ou ADMIN_PASSWORD não configurada.</p><a href='/login'>Voltar</a>""", 401
    return """
    <!doctype html><html lang="pt-br"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
    <title>AutoDev AI | Login</title><link rel="stylesheet" href="/assets/css/style.css">
    <main class="login"><form method="post" class="panel"><span class="eyebrow">AUTODEV AI</span>
    <h1>Acesso administrativo</h1><p>Entre para acompanhar os relatos e análises.</p>
    <input type="password" name="password" placeholder="Senha administrativa" required>
    <button>Entrar</button></form></main></html>
    """

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.post("/api/reports")
def submit_report():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()[:120]
    description = str(data.get("description", "")).strip()[:3000]
    email = str(data.get("email", "")).strip()[:254]
    page_url = str(data.get("page_url", "")).strip()[:500]
    if len(title) < 4 or len(description) < 10:
        return jsonify({"error": "Informe um título e uma descrição com mais detalhes."}), 400

    report_id = create_report({
        "title": title, "description": description, "email": email,
        "page_url": page_url, "created_at": datetime.now(timezone.utc).isoformat()
    })
    return jsonify({"ok": True, "id": report_id, "message": "Relato recebido. Obrigado!"}), 201

@app.get("/api/reports")
@admin_required
def reports():
    return jsonify(list_reports())

@app.get("/api/reports/<int:report_id>")
@admin_required
def report_detail(report_id):
    item = get_report(report_id)
    if not item:
        return jsonify({"error": "Relato não encontrado"}), 404
    return jsonify(item)

@app.post("/api/reports/<int:report_id>/analyze")
@admin_required
def analyze(report_id):
    item = get_report(report_id)
    if not item:
        return jsonify({"error": "Relato não encontrado"}), 404
    result = analyze_report(item)
    update_report(report_id, {
        "status": "analyzed",
        "severity": result["severity"],
        "risk": result["risk"],
        "analysis": result["analysis"]
    })
    return jsonify(result)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "AutoDev AI"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG") == "1")
