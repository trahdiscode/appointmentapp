import streamlit as st

# ---------- PAGE CONFIG (MUST BE FIRST) ----------
st.set_page_config(page_title="Parking Slot Booking", layout="centered")

from streamlit_autorefresh import st_autorefresh
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, date, timedelta

# ---------- AUTO REFRESH (REAL TIME) ----------
st_autorefresh(interval=5000, key="refresh")

st.title("🅿️ College Parking Slot Booking System")

# ---------- DARK MODE + BACKGROUND ANIMATION CSS ----------
st.markdown("""
<style>
/* Base UI */
.stApp {
    background-color: #0f1117;
    color: #e6e6e6;
    font-family: "Segoe UI", sans-serif;
    position: relative;
    z-index: 1;
}

section[data-testid="stVerticalBlock"] > div {
    background-color: #161b22;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    position: relative;
    z-index: 2;
}

/* Slot grid */
.slot-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    max-width: 600px;
}

.slot-box {
    text-align: center;
    padding: 14px 0;
    border-radius: 6px;
    font-weight: 700;
}

.free { background-color: #238636; }
.busy { background-color: #da3633; }

/* ---- Background car animation ---- */
.car {
    position: fixed;
    bottom: 40px;
    left: -60px;
    font-size: 40px;
    opacity: 0.08;
    animation: drive 30s linear infinite;
    z-index: 0;
    pointer-events: none;
}

.car.car2 {
    bottom: 120px;
    font-size: 32px;
    animation-duration: 40s;
}

@keyframes drive {
    from { left: -60px; }
    to   { left: 110%; }
}
</style>
""", unsafe_allow_html=True)

# ---------- BACKGROUND ANIMATION ELEMENTS ----------
st.markdown("""
<div class="car">🚗</div>
<div class="car car2">🚙</div>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("parking_v4.db", check_same_thread=False)
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
    slot_number TEXT NOT NULL,
    start_datetime TEXT NOT NULL,
    end_datetime TEXT NOT NULL,
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
for key in ("user_id", "vehicle_number"):
    if key not in st.session_state:
        st.session_state[key] = None

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
                st.error("Invalid username or password")

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

# ---------- PARKING SLOTS ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# ---------- REAL-TIME AVAILABILITY ----------
st.subheader("📊 Live Slot Availability (Now)")

now = datetime.now().strftime("%Y-%m-%d %H:%M")

cur.execute("""
SELECT slot_number FROM bookings
WHERE ? BETWEEN start_datetime AND end_datetime
""", (now,))

occupied = {r[0] for r in cur.fetchall()}

grid_html = "<div class='slot-grid'>"
for s in slots:
    cls = "busy" if s in occupied else "free"
    grid_html += f"<div class='slot-box {cls}'>{s}</div>"
grid_html += "</div>"

st.markdown(grid_html, unsafe_allow_html=True)

# ---------- BOOK SLOT ----------
st.subheader("Book Parking Slot")

with st.form("book"):
    st.text_input("Vehicle Number", value=st.session_state.vehicle_number, disabled=True)
    booking_date = st.date_input("Entry Date", min_value=date.today())
    entry_time = st.time_input("Entry Time", value=datetime.now().time())
    exit_time = st.time_input("Exit Time")
    slot = st.selectbox("Slot", slots)
    ok = st.form_submit_button("Book")

    if ok:
        start_dt = datetime.combine(booking_date, entry_time)
        end_dt = datetime.combine(booking_date, exit_time)

        shifted = False
        if exit_time <= entry_time:
            end_dt += timedelta(days=1)
            shifted = True

        cur.execute("""
        SELECT 1 FROM bookings
        WHERE slot_number=?
        AND NOT (end_datetime <= ? OR start_datetime >= ?)
        """, (
            slot,
            start_dt.strftime("%Y-%m-%d %H:%M"),
            end_dt.strftime("%Y-%m-%d %H:%M")
        ))

        if cur.fetchone():
            st.error("Slot is occupied during this time range")
        else:
            cur.execute("""
            INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime)
            VALUES (?, ?, ?, ?)
            """, (
                st.session_state.user_id,
                slot,
                start_dt.strftime("%Y-%m-%d %H:%M"),
                end_dt.strftime("%Y-%m-%d %H:%M")
            ))
            conn.commit()

            if shifted:
                st.warning("Exit time is earlier than entry time. Exit date shifted to next day.")

            st.success("Slot booked successfully")

# ---------- MY BOOKINGS ----------
st.subheader("My Bookings")

cur.execute("""
SELECT slot_number, start_datetime, end_datetime
FROM bookings
WHERE user_id=?
ORDER BY start_datetime DESC
""", (st.session_state.user_id,))

rows = cur.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["Slot", "Start", "End"])
    st.dataframe(df, hide_index=True)
else:
    st.info("No bookings yet")
