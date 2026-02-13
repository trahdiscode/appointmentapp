import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date
from streamlit_autorefresh import st_autorefresh

# ---------- AUTO REFRESH (REAL TIME) ----------
st_autorefresh(interval=5000, key="refresh")

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="centered")
st.title("🅿️ College Parking Slot Booking System")

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
.slot {
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
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def get_user(u, p):
    cur.execute(
        "SELECT id, vehicle_number FROM users WHERE username=? AND password_hash=?",
        (u, hash_password(p))
    )
    return cur.fetchone()

def create_user(u, p):
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (u, hash_password(p))
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
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(u, p)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.vehicle_number = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Register"):
            if create_user(u, p):
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
    v = st.text_input("Enter Vehicle Number (one time)")
    if st.button("Save Vehicle Number"):
        cur.execute(
            "UPDATE users SET vehicle_number=? WHERE id=?",
            (v.upper(), st.session_state.user_id)
        )
        conn.commit()
        st.session_state.vehicle_number = v.upper()
        st.rerun()
    st.stop()

# ---------- SLOTS ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# ---------- REAL-TIME AVAILABILITY ----------
st.subheader("📊 Live Slot Availability (Today)")

today = date.today().strftime("%d/%m/%Y")
cur.execute(
    "SELECT slot_number FROM bookings WHERE parking_date=?",
    (today,)
)
occupied = {r[0] for r in cur.fetchall()}

for s in slots:
    if s in occupied:
        st.markdown(f"<div class='slot busy'>{s}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='slot free'>{s}</div>", unsafe_allow_html=True)

# ---------- BOOK SLOT ----------
st.subheader("Book Parking Slot")

with st.form("book"):
    st.text_input("Vehicle Number", value=st.session_state.vehicle_number, disabled=True)
    d = st.date_input("Date", min_value=date.today())
    t = st.time_input("Entry Time")
    s = st.selectbox("Slot", slots)
    ok = st.form_submit_button("Book")

    if ok:
        cur.execute(
            "SELECT 1 FROM bookings WHERE parking_date=? AND slot_number=?",
            (d.strftime("%d/%m/%Y"), s)
        )
        if cur.fetchone():
            st.error("Slot already booked")
        else:
            cur.execute(
                "INSERT INTO bookings (user_id, parking_date, entry_time, slot_number) VALUES (?, ?, ?, ?)",
                (st.session_state.user_id, d.strftime("%d/%m/%Y"), t.strftime("%H:%M"), s)
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
    df = pd.DataFrame(rows, columns=["Date", "Time", "Slot"])
    st.dataframe(df, hide_index=True)
else:
    st.info("No bookings yet")
