import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).resolve().parent.parent / "autodev.db"))

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                email TEXT,
                page_url TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                severity TEXT,
                risk TEXT,
                analysis TEXT
            )
        """)

def create_report(data):
    with connect() as conn:
        cur = conn.execute("""
            INSERT INTO reports (title, description, email, page_url, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data["title"], data["description"], data["email"], data["page_url"], data["created_at"]))
        return cur.lastrowid

def list_reports():
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, title, description, email, page_url, created_at, status, severity, risk, analysis
            FROM reports ORDER BY id DESC
        """).fetchall()
        return [dict(row) for row in rows]

def get_report(report_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        return dict(row) if row else None

def update_report(report_id, fields):
    allowed = {"status", "severity", "risk", "analysis"}
    clean = {k: v for k, v in fields.items() if k in allowed}
    if not clean:
        return
    assignments = ", ".join(f"{key} = ?" for key in clean)
    with connect() as conn:
        conn.execute(
            f"UPDATE reports SET {assignments} WHERE id = ?",
            (*clean.values(), report_id)
        )
