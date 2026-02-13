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
h1, h2, h3 { color: #ffffff; font-weight: 600; }
section[data-testid="stVerticalBlock"] > div {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 18px;
}
input, textarea, select {
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
}
button:hover { background-color: #2ea043 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🅿️ College Parking Slot Booking")

# ---------- DATABASE ----------
conn = sqlite3.connect("parking.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    vehicle_number TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
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
        "SELECT id, vehicle_number FROM users WHERE username=? AND password_hash=?",
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
    st.session_state.vehicle_number = None

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
                st.session_state.vehicle_number = user[1]
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
    st.session_state.vehicle_number = None
    st.rerun()

# ---------- SET VEHICLE NUMBER (ONCE) ----------
if not st.session_state.vehicle_number:
    st.subheader("Enter Vehicle Number (One Time)")
    vehicle_input = st.text_input("Vehicle Number (e.g. TN01AB1234)")

    if st.button("Save Vehicle Number"):
        if vehicle_input.strip() == "":
            st.error("Vehicle number cannot be empty")
        else:
            cur.execute(
                "UPDATE users SET vehicle_number=? WHERE id=?",
                (vehicle_input.upper(), st.session_state.user_id)
            )
            conn.commit()
            st.session_state.vehicle_number = vehicle_input.upper()
            st.success("Vehicle number saved")
            st.rerun()

    st.stop()

# ---------- PREDEFINED SLOTS ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# ---------- ADD BOOKING ----------
st.subheader("Book Parking Slot")

with st.form("booking_form", clear_on_submit=True):
    st.text_input("Vehicle Number", value=st.session_state.vehicle_number, disabled=True)
    parking_date = st.date_input("Parking Date", min_value=date.today())
    entry_time = st.time_input("Entry Time")
    slot_number = st.selectbox("Select Slot", slots)

    submit = st.form_submit_button("Book Slot")

    if submit:
        cur.execute(
            "SELECT 1 FROM bookings WHERE parking_date=? AND slot_number=?",
            (parking_date.strftime("%d/%m/%Y"), slot_number)
        )
        if cur.fetchone():
            st.error(f"Slot {slot_number} is already booked")
        else:
            cur.execute(
                "INSERT INTO bookings (user_id, parking_date, entry_time, slot_number) VALUES (?, ?, ?, ?)",
                (
                    st.session_state.user_id,
                    parking_date.strftime("%d/%m/%Y"),
                    entry_time.strftime("%H:%M"),
                    slot_number
                )
            )
            conn.commit()
            st.success(f"Slot {slot_number} booked successfully")

# ---------- SHOW BOOKINGS ----------
st.subheader("My Bookings")

cur.execute(
    "SELECT parking_date, entry_time, slot_number FROM bookings WHERE user_id=?",
    (st.session_state.user_id,)
)
rows = cur.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["Date", "Entry Time", "Slot"])
    df.insert(0, "No", [str(i) for i in range(1, len(df) + 1)])
    st.dataframe(df, hide_index=True)
else:
    st.info("No bookings yet")
