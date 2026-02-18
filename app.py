import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

from streamlit_autorefresh import st_autorefresh
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ---------- AUTO REFRESH ----------
# st_autorefresh(interval=5000, key="refresh")

# ---------- "15-YEAR-OLD PRO" UI STYLESHEET ----------
st.markdown("""
<style>
/* Import Google Font: Inter - The standard for modern UI */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* --- Root Variables: A modern, dev-centric palette --- */
:root {
    --font-family: 'Inter', sans-serif;
    --color-bg: #11111B; /* A deep, near-black space color */
    --color-text-primary: #E5E7EB;
    --color-text-secondary: #9CA3AF;
    --color-border: rgba(255, 255, 255, 0.1); /* Subtle border for glass effect */
    --color-accent: #8B5CF6; /* A vibrant, electric violet */
    --color-accent-hover: #7C3AED;
    --border-radius-lg: 1rem;
    --border-radius-md: 0.5rem;
}

/* --- Base App Styling --- */
.stApp {
    background-color: var(--color-bg);
    font-family: var(--font-family);
}

/* --- Typography & Headings --- */
h1, h2, h3 {
    color: var(--color-text-primary);
    font-family: var(--font-family);
}
h1 {
    font-weight: 700;
    font-size: 1.8rem;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
}
h2 {
    font-weight: 600;
    font-size: 1.4rem;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
}
h3 {
    font-weight: 600;
    font-size: 1.15rem;
    margin-top: 2rem;
    margin-bottom: 0.5rem;
}

/* --- UI Elements: Inputs & Buttons --- */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stSelectbox > div > div > button {
    background-color: rgba(31, 41, 55, 0.3);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    transition: all 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTimeInput > div > div > input:focus,
.stSelectbox > div > div > button:focus {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3);
    outline: none;
}

.stButton > button {
    font-weight: 500;
    background-color: rgba(31, 41, 55, 0.5);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: rgba(55, 65, 81, 0.5);
    border-color: rgba(255, 255, 255, 0.2);
}

.stButton > button.primary {
    background-color: var(--color-accent);
    border-color: var(--color-accent);
    color: white;
}
.stButton > button.primary:hover {
    background-color: var(--color-accent-hover);
    border-color: var(--color-accent-hover);
}

/* --- Glassmorphism Card Style for Metric & Status --- */
div[data-testid="stMetric"],
div[data-testid="stAlert"] {
    background: rgba(30, 30, 42, 0.5); /* Semi-transparent background */
    backdrop-filter: blur(12px); /* The frosted glass effect */
    -webkit-backdrop-filter: blur(12px); /* For Safari */
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    height: 100%;
}
div[data-testid="stAlert"][data-baseweb="alert-success"] {
    background-color: rgba(22, 163, 74, 0.1);
    border-color: rgba(34, 197, 94, 0.2);
}
div[data-testid="stAlert"][data-baseweb="alert-info"] {
    background-color: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.2);
}

/* --- Slot Grid --- */
.slot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
    margin-bottom: 2rem;
}
.slot {
    padding: 1rem 0;
    text-align: center;
    border-radius: var(--border-radius-md);
    font-weight: 600;
    color: white;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}
.slot:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.7);
}
.free { background-color: #16a34a; }
.busy { background-color: #dc2626; }
.mine {
    background-color: var(--color-accent);
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.7);
}
small {
    font-weight: 500;
    font-size: 0.75rem;
    opacity: 0.9;
}

</style>
""", unsafe_allow_html=True)

# (All Python code below is identical to the previous professional dark theme, as it is functionally correct.)
# ---------- DATABASE ----------
conn = sqlite3.connect("parking_v4.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, vehicle_number TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, slot_number TEXT NOT NULL, start_datetime TEXT NOT NULL, end_datetime TEXT NOT NULL)")
conn.commit()
# ---------- HELPERS ----------
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()
def get_user(u, p):
    cur.execute("SELECT id, vehicle_number FROM users WHERE username=? AND password_hash=?", (u, hash_password(p)))
    return cur.fetchone()
def create_user(u, p):
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (u, hash_password(p)))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
# ---------- SESSION ----------
for k in ("user_id", "vehicle_number"):
    if k not in st.session_state: st.session_state[k] = None

# ---------- AUTH PAGE ----------
if st.session_state.user_id is None:
    st.title("🅿️ Parking Slot Booking System")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            user = get_user(u, p)
            if user:
                st.session_state.user_id, st.session_state.vehicle_number = user[0], user[1]
                st.rerun()
            else: st.error("Invalid credentials")
    with tab2:
        u = st.text_input("New Username", key="reg_user")
        p = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            if create_user(u, p): st.success("Account created. Login now.")
            else: st.error("Username already exists")
    st.stop()

# ---------- MAIN APP LAYOUT ----------

# --- HEADER ---
col1, col2 = st.columns([8, 1])
with col1:
    st.title("🅿️ Parking Slot Booking")
with col2:
    if st.button("Logout"):
        st.session_state.user_id, st.session_state.vehicle_number = None, None
        st.rerun()

# --- VEHICLE NUMBER ---
if st.session_state.vehicle_number is None:
    v = st.text_input("Enter Vehicle Number (one time requirement)")
    if st.button("Save Vehicle Number", type="primary"):
        cur.execute("UPDATE users SET vehicle_number=? WHERE id=?", (v.upper(), st.session_state.user_id))
        conn.commit()
        st.session_state.vehicle_number = v.upper()
        st.rerun()
    st.stop()

# --- DASHBOARD SECTION ---
st.header("Dashboard Overview")

# --- STATUS CARDS ---
col1, col2 = st.columns(2)
with col1:
    now_dt = datetime.now()
    cur.execute("SELECT slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M")))
    active = cur.fetchone()
    
    if active:
        slot, _, end = active
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M")
        remaining = end_time - now_dt
        st.success(f"""
        **Currently Parked**\n
        **Slot:** {slot}\n
        **Until:** {end_time.strftime("%I:%M %p")}\n
        **Time Remaining:** {str(remaining).split('.')[0]}
        """)
    else:
        st.info("No active parking session.")

with col2:
    cur.execute("SELECT COUNT(*) FROM bookings")
    total = cur.fetchone()[0]
    st.metric("Total Lifetime Bookings", total)

# --- LIVE AVAILABILITY SECTION ---
st.header("Live Slot Availability")
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]
now = datetime.now().strftime("%Y-%m-%d %H:%M")
cur.execute("SELECT slot_number FROM bookings WHERE? BETWEEN start_datetime AND end_datetime", (now,))
occupied = {r[0] for r in cur.fetchall()}
cur.execute("SELECT slot_number FROM bookings WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime", (st.session_state.user_id, now))
mine = {r[0] for r in cur.fetchall()}

grid = "<div class='slot-grid'>"
for s in slots:
    cls, label = ("mine", "YOURS") if s in mine else (("busy", "BUSY") if s in occupied else ("free", "FREE"))
    grid += f"<div class='slot {cls}'>{s}<br><small>{label}</small></div>"
grid += "</div>"
st.markdown(grid, unsafe_allow_html=True)

# --- BOOKING SECTION ---
st.header("Book a New Parking Slot")
booking_date = st.date_input("Select Date", min_value=date.today())
col1, col2 = st.columns(2)
with col1:
    entry_time = st.time_input("Select Entry Time", value=datetime.now().replace(second=0, microsecond=0).time())
with col2:
    exit_time = st.time_input("Select Exit Time")

start_dt, end_dt = datetime.combine(booking_date, entry_time), datetime.combine(booking_date, exit_time)
if exit_time <= entry_time:
    end_dt += timedelta(days=1)
    st.warning("Exit time is before entry. Booking will extend to the next day.", icon="⚠️")

cur.execute("SELECT slot_number FROM bookings WHERE NOT (end_datetime <=? OR start_datetime >=?)", (start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
blocked = {r[0] for r in cur.fetchall()}
available = [s for s in slots if s not in blocked]

if available:
    slot = st.selectbox("Available Slots", available)
    if st.button("Confirm Booking", type="primary", use_container_width=True):
        cur.execute("SELECT id FROM bookings WHERE user_id=? AND NOT (end_datetime <=? OR start_datetime >=?)", (st.session_state.user_id, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
        if cur.fetchone():
            st.error("You already have an overlapping booking.", icon="🚫")
        else:
            cur.execute("INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)", (st.session_state.user_id, slot, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success(f"Slot {slot} booked successfully!", icon="✅")
            st.rerun()
else:
    st.error("No slots available for the selected time frame.", icon="🚫")
