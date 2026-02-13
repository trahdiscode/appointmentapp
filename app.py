import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="centered")
st.title("🅿️ College Parking Slot Booking System")

# ---------- AUTO REFRESH (REAL-TIME) ----------
st.autorefresh(interval=5000, key="refresh")

# ---------- DARK MODE CSS ----------
st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
    color: #e6e6e6;
    font-family: "Segoe UI", sans-serif;
}
section[data-testid="stVerticalBlock"] > div {
    background-color: #161b22;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 16px;
}
.slot-box {
    display: inline-block;
    padding: 10px 14px;
    margin: 6px;
    border-radius: 6px;
    font-weight: 600;
}
.free { background-color: #238636; color: white; }
.busy { background-color: #da3633; color: white; }
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("parking_v2.db", check_same_thread=False)
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

# ---------- SESSION STATE ----------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "vehicle_number" not in st.session_state:
    st.session_state.vehicle_number = None

# ---------- AUTH ----------
if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.vehicle_number = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if create_user(username, password):
                st.success("Account created. Login now.")
            else:
                st.error("Username already exists")

    st.stop()

# ---------- LOGOUT ----------
if st.button("Logout"):
    st.session_state.user_id = None
    st.session_state.vehicle_number = None
    st.rerun()

# ---------- VEHICLE NUMBER ----------
if st.session_state.vehicle_number is None:
    vehicle = st.text_input("Enter Vehicle Number (one time)")
    if st.button("Save Vehicle Number"):
        cur.execute(
            "UPDATE users SET vehicle_number=? WHERE id=?",
            (vehicle.upper(), st.session_state.user_id)
        )
        conn.commit()
        st.session_state.vehicle_number = vehicle.upper()
        st.rerun()
    st.stop()

# ---------- PARKING SLOTS ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# ---------- REAL-TIME SLOT AVAILABILITY ----------
st.subheader("📊 Live Slot Availability (Today)")

today = date.today().strftime("%d/%m/%Y")
cur.execute(
    "SELECT slot_number FROM bookings WHERE parking_date=?",
    (today,)
)
occupied = {row[0] for row in cur.fetchall()}

for slot in slots:
    if slot in occupied:
        st.markdown(f"<div class='slot-box busy'>{slot}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='slot-box free'>{slot}</div>", unsafe_allow_html=True)

# ---------- BOOK SLOT ----------
st.subheader("Book Parking Slot")

with st.form("booking_form", clear_on_submit=True):
    st.text_input("Vehicle Number", value=st.session_state.vehicle_number, disabled=True)
    parking_date = st.date_input("Date", min_value=date.today())
    entry_time = st.time_input("Entry Time")
    slot = st.selectbox("Select Slot", slots)
    submit = st.form_submit_button("Book Slot")

    if submit:
        cur.execute(
            "SELECT 1 FROM bookings WHERE parking_date=? AND slot_number=?",
            (parking_date.strftime("%d/%m/%Y"), slot)
        )
        if cur.fetchone():
            st.error("Slot already booked")
        else:
            cur.execute(
                "INSERT INTO bookings (user_id, parking_date, entry_time, slot_number) VALUES (?, ?, ?, ?)",
                (st.session_state.user_id,
                 parking_date.strftime("%d/%m/%Y"),
                 entry_time.strftime("%H:%M"),
                 slot)
            )
            conn.commit()
            st.success("Slot booked")

# ---------- MY BOOKINGS ----------
st.subheader("My Bookings")
cur.execute(
    "SELECT parking_date, entry_time, slot_number FROM bookings WHERE user_id=?",
    (st.session_state.user_id,)
)
rows = cur.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["Date", "Entry Time", "Slot"])
    st.dataframe(df, hide_index=True)
else:
    st.info("No bookings yet")
