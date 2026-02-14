import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

from streamlit_autorefresh import st_autorefresh
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ---------- AUTO REFRESH ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- DARK MODE CSS ----------
st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
    color: #e6e6e6;
    font-family: "Segoe UI", sans-serif;
}
.slot-grid {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 10px;
    max-width: 900px;
}
.slot {
    padding: 14px 0;
    text-align: center;
    border-radius: 6px;
    font-weight: 700;
    color: white;
}
.free { background-color: #238636; }
.busy { background-color: #da3633; }
.mine { background-color: #1f6feb; }
small { font-weight: 400; opacity: 0.9; }

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 10px;
}

.subtle-line {
    height: 2px;
    background: linear-gradient(90deg, #1f6feb, transparent);
    margin-bottom: 20px;
}
</style>
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
    end_datetime TEXT NOT NULL
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

# ---------- SESSION ----------
for k in ("user_id", "vehicle_number"):
    if k not in st.session_state:
        st.session_state[k] = None

import time

if "error_message" not in st.session_state:
    st.session_state.error_message = None

if "error_time" not in st.session_state:
    st.session_state.error_time = None
# ---------- AUTH ----------
if st.session_state.user_id is None:
    st.markdown("## 🅿️ Parking Slot Booking")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            user = get_user(u, p)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.vehicle_number = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username", key="reg_user")
        p = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            if create_user(u, p):
                st.success("Account created. Login now.")
            else:
                st.error("Username already exists")

    st.stop()

# ---------- HEADER ----------
st.markdown("""
<div style='font-size:38px; font-weight:800;'>
🅿 Parking Slot Booking
</div>
<div style='font-size:16px; opacity:0.6; margin-bottom:20px;'>
Faculty Parking Management System
</div>
<hr style='border:1px solid #1f6feb; opacity:0.3;'>
""", unsafe_allow_html=True)

# ---------- VEHICLE NUMBER ----------
if st.session_state.vehicle_number is None:
    v = st.text_input("Enter Vehicle Number (one time)")
    if st.button("Save Vehicle Number", type="primary"):
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

st.markdown("<div class='main-title'>Parking Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtle-line'></div>", unsafe_allow_html=True)

st.divider()

# ---------- ACTIVE BOOKING STATUS ----------
now_dt = datetime.now()

cur.execute("""
SELECT slot_number, start_datetime, end_datetime
FROM bookings
WHERE user_id=? AND ? BETWEEN start_datetime AND end_datetime
""", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M")))

active = cur.fetchone()

col1, col2 = st.columns([2, 1])

with col1:
   if active:
        slot, start, end = active
    
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M")
        remaining = end_time - now_dt
    
        st.success(f"""
    🚗 **Currently Parked**
    
    **Slot:** {slot}  
    **Until:** {end_time.strftime("%H:%M")}  
    **Time Remaining:** {str(remaining).split('.')[0]}
    """)
    
        # 🔴 Cancel Booking Button
        if st.button("Cancel Booking", use_container_width=True):
    
            cur.execute("""
            DELETE FROM bookings
            WHERE user_id=? AND slot_number=? AND start_datetime=? AND end_datetime=?
            """, (
                st.session_state.user_id,
                slot,
                start,
                end
            ))
    
            conn.commit()
    
            st.success("Booking cancelled successfully.")
            st.rerun()
    else:
        st.info("🟢 No active parking session")

with col2:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute("""
    SELECT slot_number FROM bookings
    WHERE ? BETWEEN start_datetime AND end_datetime
    """, (now,))

    occupied = {r[0] for r in cur.fetchall()}

    available_count = len(slots) - len(occupied)

    st.metric("Available Slots", available_count)
    
# ---------- LIVE AVAILABILITY ----------
st.divider()
st.markdown("<div class='section-title'>Live Slot Overview</div>", unsafe_allow_html=True)
st.caption("Real-time availability")

now = datetime.now().strftime("%Y-%m-%d %H:%M")

cur.execute("""
SELECT slot_number FROM bookings
WHERE ? BETWEEN start_datetime AND end_datetime
""", (now,))
occupied = {r[0] for r in cur.fetchall()}

cur.execute("""
SELECT slot_number FROM bookings
WHERE user_id=? AND ? BETWEEN start_datetime AND end_datetime
""", (st.session_state.user_id, now))
mine = {r[0] for r in cur.fetchall()}

grid = "<div class='slot-grid'>"
for s in slots:
    if s in mine:
        cls, label = "mine", "YOURS"
    elif s in occupied:
        cls, label = "busy", "BUSY"
    else:
        cls, label = "free", "FREE"

    grid += f"<div class='slot {cls}'>{s}<br><small>{label}</small></div>"
grid += "</div>"

st.markdown(grid, unsafe_allow_html=True)

# ---------- BOOK SLOT ----------
st.divider()
st.markdown("<div class='section-title'>Book Parking</div>", unsafe_allow_html=True)
if st.session_state.error_message:
    elapsed = time.time() - st.session_state.error_time

    if elapsed < 7:
        st.error(st.session_state.error_message)
    else:
        st.session_state.error_message = None
        st.session_state.error_time = None
col1, col2, col3 = st.columns(3)

with col1:
    booking_date = st.date_input("Date", min_value=date.today())

with col2:
    entry_time = st.time_input(
        "Entry Time",
        value=datetime.now().replace(second=0, microsecond=0).time()
    )

with col3:
    exit_time = st.time_input("Exit Time")

start_dt = datetime.combine(booking_date, entry_time)
end_dt = datetime.combine(booking_date, exit_time)

overnight = False
if exit_time <= entry_time:
    overnight = True
    st.caption("Overnight booking")

if overnight:
    end_dt += timedelta(days=1)

cur.execute("""
SELECT slot_number FROM bookings
WHERE NOT (end_datetime <= ? OR start_datetime >= ?)
""", (
    start_dt.strftime("%Y-%m-%d %H:%M"),
    end_dt.strftime("%Y-%m-%d %H:%M")
))

blocked = {r[0] for r in cur.fetchall()}
available = [s for s in slots if s not in blocked]

if available:
    slot = st.selectbox("Available Slots", available)
else:
    st.error("No slots available")
    slot = None

if st.button("Confirm Booking", use_container_width=True):

    if slot is None:
        st.stop()

    cur.execute("""
    SELECT id FROM bookings
    WHERE user_id=?
    AND NOT (end_datetime <= ? OR start_datetime >= ?)
    """, (
        st.session_state.user_id,
        start_dt.strftime("%Y-%m-%d %H:%M"),
        end_dt.strftime("%Y-%m-%d %H:%M")
    ))

    if cur.fetchone():
        st.session_state.error_message = "You already have a booking during this time."
        st.session_state.error_time = time.time()
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
        st.success(f"Slot {slot} booked successfully")
        st.rerun()
