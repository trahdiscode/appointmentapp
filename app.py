import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Appointment Manager", layout="centered")

# ---------- CLEAN DARK MODE CSS ----------
st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #0f1117;
    color: #e6e6e6;
    font-family: "Segoe UI", sans-serif;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff;
    font-weight: 600;
}

/* Containers */
section[data-testid="stVerticalBlock"] > div {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 18px;
}

/* Inputs */
input, textarea {
    background-color: #0f1117 !important;
    color: #e6e6e6 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}

/* Buttons */
button {
    background-color: #238636 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}

button:hover {
    background-color: #2ea043 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #e6e6e6 !important;
    font-weight: 500;
}

/* Dataframe */
.stDataFrame {
    background-color: #0f1117;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("📅 Appointment Manager")

# ---------- DATABASE ----------
conn = sqlite3.connect("app_v2.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()

# ---------- HELPERS ----------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username, password):
    cur.execute(
        "SELECT id FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    return cur.fetchone()

def create_user(username, password):
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ---------- SESSION ----------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- AUTH ----------
if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = get_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            if username.strip() == "" or password.strip() == "":
                st.error("Fields cannot be empty")
            elif create_user(username, password):
                st.success("Account created. Login now.")
            else:
                st.error("Username already exists")

    st.stop()

# ---------- LOGOUT ----------
if st.button("Logout"):
    st.session_state.user_id = None
    st.rerun()

# ---------- ADD APPOINTMENT ----------
st.subheader("Add Appointment")

with st.form("appointment_form", clear_on_submit=True):
    title = st.text_input("Title")
    app_date = st.date_input("Date", min_value=date.today())
    app_time = st.time_input("Time")
    description = st.text_area("Description")

    submit = st.form_submit_button("Add Appointment")

    if submit:
        if title.strip() == "":
            st.error("Title cannot be empty")
        else:
            cur.execute(
                "INSERT INTO appointments (user_id, title, date, time, description) VALUES (?, ?, ?, ?, ?)",
                (
                    st.session_state.user_id,
                    title,
                    app_date.strftime("%d/%m/%Y"),
                    app_time.strftime("%H:%M"),
                    description
                )
            )
            conn.commit()
            st.success("Appointment added")

# ---------- SHOW APPOINTMENTS ----------
st.subheader("Your Appointments")

cur.execute(
    "SELECT title, date, time, description FROM appointments WHERE user_id=?",
    (st.session_state.user_id,)
)

rows = cur.fetchall()

if not rows:
    st.info("No appointments added yet")
else:
    df = pd.DataFrame(rows, columns=["Title", "Date", "Time", "Description"])
    df.insert(0, "No", [str(i) for i in range(1, len(df) + 1)])
    st.dataframe(df, hide_index=True)
