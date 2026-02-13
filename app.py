import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="centered")

# ---------- DARK MODE CSS ----------
st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
    color: #e6e6e6;
    font-family: "Segoe UI", sans-serif;
}

h1, h2, h3 {
    color: #ffffff;
    font-weight: 600;
}

section[data-testid="stVerticalBlock"] > div {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 18px;
}

input, textarea {
    background-color: #0f1117 !important;
    color: #e6e6e6 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}

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

button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #e6e6e6 !important;
}

.stDataFrame {
    background-color: #0f1117;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("🅿️ Parking Slot Booking System")

# ---------- DATABASE ----------
conn = sqlite3.connect("parking.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vehicle_number TEXT NOT NULL,
    parking_date TEXT NOT NULL,
    entry_time TEXT NOT NULL,
    slot_number TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()

# ---------- HELPERS ----------
def hash_password(password):
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

# ---------- ADD BOOKING ----------
st.subheader("Book a Parking Slot")

with st.form("booking_form", clear_on_submit=True):
    vehicle_number = st.text_input("Vehicle Number (e.g. TN01AB1234)")
    parking_date = st.date_input("Parking Date", min_value=date.today())
    entry_time = st.time_input("Entry Time")
    slot_number = st.text_input("Slot Number")

    submit = st.form_submit_button("Book Slot")

    if submit:
        if vehicle_number.strip() == "" or slot_number.strip() == "":
            st.error("Vehicle number and slot number are required")
        else:
            cur.execute(
                """
                INSERT INTO bookings (user_id, vehicle_number, parking_date, entry_time, slot_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    st.session_state.user_id,
                    vehicle_number.upper(),
                    parking_date.strftime("%d/%m/%Y"),
                    entry_time.strftime("%H:%M"),
                    slot_number.upper()
                )
            )
            conn.commit()
            st.success("Parking slot booked successfully")

# ---------- SHOW BOOKINGS ----------
st.subheader("My Parking Bookings")

cur.execute(
    """
    SELECT vehicle_number, parking_date, entry_time, slot_number
    FROM bookings
    WHERE user_id=?
    """,
    (st.session_state.user_id,)
)

rows = cur.fetchall()

if not rows:
    st.info("No parking bookings yet")
else:
    df = pd.DataFrame(
        rows,
        columns=["Vehicle Number", "Date", "Entry Time", "Slot"]
    )
    df.insert(0, "No", [str(i) for i in range(1, len(df) + 1)])
    st.dataframe(df, hide_index=True)
