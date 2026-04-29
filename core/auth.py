import psycopg2
import bcrypt

DB_URL = "YOUR_POSTGRES_URL"


def get_conn():
    return psycopg2.connect(DB_URL)


def create_user(email, password):
    conn = get_conn()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cur.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (email, hashed)
    )

    conn.commit()
    conn.close()


def login_user(email, password):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, password, plan FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    conn.close()

    if not user:
        return None

    user_id, hashed, plan = user

    if bcrypt.checkpw(password.encode(), hashed.encode()):
        return {"id": user_id, "plan": plan}

    return None