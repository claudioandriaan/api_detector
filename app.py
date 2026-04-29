import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
import sys
import asyncio

from core.browser import capture_api_calls
from core.analyzer import is_valid_api, classify, detect_pagination
from core.validator import test_endpoint
from core.analytics import get_visitor_info

# =========================================================
# SYSTEM FIX (Windows only)
# =========================================================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# =========================================================
# DATABASE HELPERS
# =========================================================
DB_NAME = "app.db"

def get_conn():
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        url TEXT,
        ip TEXT,
        country TEXT,
        city TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

def add_column_if_missing():
    conn = get_conn()
    c = conn.cursor()

    c.execute("PRAGMA table_info(visits)")
    columns = [col[1] for col in c.fetchall()]

    if "url" not in columns:
        c.execute("ALTER TABLE visits ADD COLUMN url TEXT")

    conn.commit()
    conn.close()
    
add_column_if_missing()

# =========================================================
# ADMIN SETUP (RUN ONCE ONLY)
# =========================================================
def ensure_admin():
    conn = get_conn()
    c = conn.cursor()

    email = "claudio.andriaan@gmail.com"
    password = "admin123"

    c.execute("SELECT id FROM users WHERE email=?", (email,))
    exists = c.fetchone()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    if not exists:
        c.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, hashed, "admin")
        )

    conn.commit()
    conn.close()

ensure_admin()

# =========================================================
# AUTH
# =========================================================
def create_user(email, password, role="user"):
    conn = get_conn()
    c = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        c.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, hashed, role)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT email, password, role FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if not user:
        return None

    stored_password = user[1].encode()

    if bcrypt.checkpw(password.encode(), stored_password):
        return {"email": user[0], "role": user[2]}

    return None

def log_visit(email, url):
    conn = get_conn()
    c = conn.cursor()

    info = get_visitor_info()

    c.execute("""
    INSERT INTO visits (user_email, url, ip, country, city, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email,
        url,
        info["ip"],
        info["country"],
        info["city"],
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

# =========================================================
# SESSION
# =========================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================================================
# LOGIN / REGISTER
# =========================================================
if not st.session_state.user:

    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.user = user
                log_visit(email, "LOGIN")
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if create_user(email, password):
                st.success("Account created")
            else:
                st.error("User already exists")

    st.stop()

# =========================================================
# MAIN APP
# =========================================================
user = st.session_state.user

st.sidebar.write(f"👤 {user['email']}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.selectbox(
    "Navigation",
    ["🔍 Detector", "📚 Docs", "📊 Stats", "🛠 Admin", "🧾 JSON Preview"]
)

# =========================================================
# DETECTOR
# =========================================================
if menu == "🔍 Detector":

    st.title("🔍 API Detector")

    url = st.text_input("Enter website URL")

    if st.button("Detect APIs"):

        if not url:
            st.warning("Enter URL")
        else:
            log_visit(user["email"], url)

            with st.spinner("Analyzing..."):
                raw_results = capture_api_calls(url)

                results = []
                seen = set()

                for entry in raw_results:
                    if not is_valid_api(entry):
                        continue

                    if entry["url"] in seen:
                        continue

                    seen.add(entry["url"])

                    results.append({
                        "endpoint": entry["url"],
                        "type": classify(entry),
                        "method": entry["method"],
                        "reusable": test_endpoint(entry),
                        "pagination": detect_pagination(entry["url"])
                    })

            if results:
                st.success(f"{len(results)} API(s) detected")

                for api in results:
                    with st.expander(api["endpoint"]):
                        st.json(api)
            else:
                st.error("No API detected")

# =========================================================
# DOCS
# =========================================================
elif menu == "📚 Docs":

    st.title("📚 API Detector Documentation")

    st.markdown("""
## 🔍 API Detector — Overview

This tool automatically detects API endpoints from websites using Playwright.

### Features
- API interception
- Endpoint classification
- Pagination detection
- Usage tracking per user
- Admin analytics dashboard

### How it works
1. Load website
2. Capture network requests
3. Extract JSON APIs
4. Analyze endpoints

### Use cases
- Web scraping
- Reverse engineering APIs
- Data extraction
""")

# =========================================================
# STATS
# =========================================================
elif menu == "📊 Stats":

    st.title("📊 Statistics")

    conn = get_conn()
    c = conn.cursor()

    if user["role"] != "admin":

        st.subheader("👤 Your Activity")

        c.execute("""
            SELECT url, timestamp 
            FROM visits 
            WHERE user_email=? 
            ORDER BY id DESC
        """, (user["email"],))

        data = c.fetchall()

        st.metric("Total Requests", len(data))

        for row in data[:10]:
            st.write(f"🌐 {row[0]} | 🕒 {row[1]}")

    else:

        st.subheader("🛠 Admin Overview")

        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM visits")
        total_requests = c.fetchone()[0]

        col1, col2 = st.columns(2)
        col1.metric("Users", total_users)
        col2.metric("Requests", total_requests)

        st.markdown("### All Activity")

        c.execute("""
            SELECT user_email, url, timestamp
            FROM visits
            ORDER BY id DESC
            LIMIT 100
        """)

        for row in c.fetchall():
            st.write(f"👤 {row[0]} | 🌐 {row[1]} | 🕒 {row[2]}")

    conn.close()

# =========================================================
# ADMIN (EXTRA PANEL)
# =========================================================
elif menu == "🛠 Admin":

    if user["role"] != "admin":
        st.error("Access denied")
        st.stop()

    st.title("🛠 Admin Dashboard")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM visits")
    visits = c.fetchone()[0]

    st.metric("Total Users", users)
    st.metric("Total Visits", visits)

    st.markdown("### Recent Requests")

    c.execute("""
        SELECT user_email, url, timestamp
        FROM visits
        ORDER BY id DESC
        LIMIT 50
    """)

    for r in c.fetchall():
        st.write(r)

    conn.close()
elif menu == "🧾 JSON Preview":

    st.title("🧾 JSON Explorer (Tree View)")
    st.write("Paste JSON and explore it like DevTools.")

    import json
    import streamlit.components.v1 as components

    json_input = st.text_area("Paste JSON here", height=200)

    if st.button("Preview JSON"):

        if not json_input:
            st.warning("Please paste JSON")
        else:
            try:
                data = json.loads(json_input)

                st.success("JSON loaded successfully")

                # Convert JSON to string for JS
                json_str = json.dumps(data)

                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.10.0/jsoneditor.min.css" rel="stylesheet" type="text/css">
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.10.0/jsoneditor.min.js"></script>

                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                            background: #0e1117;
                        }}
                        #jsoneditor {{
                            width: 100%;
                            height: 500px;
                        }}
                    </style>
                </head>

                <body>
                    <div id="jsoneditor"></div>

                    <script>
                        const container = document.getElementById("jsoneditor");

                        const options = {{
                            mode: "tree",
                            modes: ["tree", "view", "code"],
                            search: true
                        }};

                        const editor = new JSONEditor(container, options);

                        const json = {json_str};

                        editor.set(json);
                    </script>
                </body>
                </html>
                """

                components.html(html_code, height=520, scrolling=True)

            except Exception as e:
                st.error(f"Invalid JSON: {e}")