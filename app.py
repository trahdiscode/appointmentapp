import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

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
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "vehicle_number" not in st.session_state:
    st.session_state.vehicle_number = None

# ---------- AUTH ----------
if st.session_state.user_id is None:

    st.markdown("## 🅿️ Parking Slot Booking")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
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

        if st.button("Register", use_container_width=True):
            if create_user(u, p):
                st.success("Account created. Login now.")
            else:
                st.error("Username already exists")

    st.stop()

# ---------- HEADER ----------
col1, col2, col3 = st.columns([6, 3, 1])

with col1:
    st.markdown("## 🅿️ Parking Slot Booking")

with col2:
    st.caption(f"Vehicle: **{st.session_state.vehicle_number or 'Not set'}**")

with col3:
    if st.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.vehicle_number = None
        st.rerun()

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

# ---------- SLOT LIST ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# ---------- LIVE AVAILABILITY ----------
st.subheader("📊 Live Slot Availability (Now)")

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
# ---------- BOOK SLOT ----------
st.subheader("📅 Book Parking Slot")

if "default_entry_time" not in st.session_state:
    st.session_state.default_entry_time = datetime.now().replace(second=0, microsecond=0).time()

if "default_exit_time" not in st.session_state:
    st.session_state.default_exit_time = (
        datetime.now() + timedelta(hours=1)
    ).replace(second=0, microsecond=0).time()

with st.form("booking"):

    booking_date = st.date_input("Date", min_value=date.today())

    entry_time = st.time_input(
        "Entry Time",
        value=st.session_state.default_entry_time,
        key="entry_time"
    )

    exit_time = st.time_input(
        "Exit Time",
        value=st.session_state.default_exit_time,
        key="exit_time"
    )

    # Create datetime objects
    start_dt = datetime.combine(booking_date, entry_time)
    end_dt = datetime.combine(booking_date, exit_time)

    # SHIFT LOGIC
    shifted = False
    if exit_time <= entry_time:
        end_dt += timedelta(days=1)
        shifted = True

    if shifted:
        st.warning("Exit time is earlier than entry time. Booking extends to next day.")

    # Check overlapping bookings
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
        slot = None
        st.error("No slots available for selected time")

    submit = st.form_submit_button("Confirm Booking")

    if submit and slot:
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

        st.success("Slot booked successfully")

        # Reset times after booking
        st.session_state.default_entry_time = datetime.now().replace(second=0, microsecond=0).time()
        st.session_state.default_exit_time = (
            datetime.now() + timedelta(hours=1)
        ).replace(second=0, microsecond=0).time()

        st.rerun()
        st.rerun()
