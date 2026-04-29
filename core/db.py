import sqlite3
from datetime import datetime

DB_NAME = "app.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        url TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def log_usage(session_id, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO usage (session_id, url, timestamp)
        VALUES (?, ?, ?)
    """, (session_id, url, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def get_usage(session_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT url, timestamp FROM usage
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 50
    """, (session_id,))

    rows = c.fetchall()
    conn.close()

    return rows