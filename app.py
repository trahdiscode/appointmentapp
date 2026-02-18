import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

# ---------- AUTO REFRESH (1 SECOND) ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- "15 YEARS OF EXPERIENCE" UI STYLESHEET (Simplified and Corrected) ----------
st.markdown("""
<style>
/* Import Google Font: Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* --- Root Variables --- */
:root {
    --font-family: 'Inter', sans-serif;
    --color-bg: #121212;
    --color-bg-secondary: #1A1A1A;
    --color-text-primary: #EAEAEA;
    --color-text-secondary: #A0A0A0;
    --color-border: #2A2A2A;
    --color-accent: #4A90E2; /* Blue for selection */
    --color-free: #50A86E; /* Green for free */
    --color-busy: #B9535A; /* Red for busy */
    --border-radius: 6px;
}

/* --- Base App Styling --- */
.stApp {
    background-color: var(--color-bg);
    font-family: var(--font-family);
}

/* --- Typography --- */
h1, h2, h3 { color: var(--color-text-primary); font-family: var(--font-family); letter-spacing: -0.02em; }
h1 { font-weight: 600; font-size: 1.75rem; padding-bottom: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--color-border); }
h2 { font-weight: 500; font-size: 1.25rem; color: var(--color-text-secondary); margin-top: 2.5rem; margin-bottom: 1rem; }
h3 { font-weight: 500; font-size: 1.1rem; margin-top: 2rem; margin-bottom: 0.5rem; }

/* --- Standard UI Elements --- */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input {
    background-color: var(--color-bg);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    transition: all 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTimeInput > div > div > input:focus {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
    outline: none;
}
.stButton > button.primary { background-color: var(--color-accent); border-color: var(--color-accent); color: #FFFFFF; }
.stButton > button.primary:hover { background-color: #5A9EE8; border-color: #5A9EE8; }

/* --- Card Styling --- */
div[data-testid="stMetric"], div[data-testid="stAlert"] {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    height: 100%;
}
div[data-testid="stAlert"][data-baseweb="alert-success"] { background-color: rgba(34, 129, 74, 0.1); border-color: rgba(34, 129, 74, 0.3); }
div[data-testid="stAlert"][data-baseweb="alert-info"] { background-color: rgba(74, 144, 226, 0.1); border-color: rgba(74, 144, 226, 0.3); }

/* --- Styling for st.button used as slots --- */
div[data-testid="stHorizontalBlock"] {
    gap: 0.75rem;
}
.stButton button {
    width: 100%;
    height: 60px; /* Adjusted height */
    padding: 0;
    margin: 0;
    font-size: 1.1rem; /* Larger slot number */
    font-weight: 600;
    background-color: var(--color-bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.2s ease;
}
.stButton button:hover:not(:disabled) {
    border-color: var(--color-text-secondary);
}
.stButton button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

</style>
""", unsafe_allow_html=True)

# (Database and Helper functions are unchanged)
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

# ---------- SESSION STATE INITIALIZATION ----------
if 'selected_slot' not in st.session_state:
    st.session_state.selected_slot = None

# ---------- AUTH PAGE ----------
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.title("🅿️ Parking Slot Booking System")
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
            else: st.error("Invalid credentials")
    with tab2:
        u = st.text_input("New Username", key="reg_user")
        p = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            if create_user(u, p): st.success("Account created. Login now.")
            else: st.error("Username already exists")
    st.stop()

# ---------- MAIN APP LAYOUT ----------
col1, col2 = st.columns([8, 1])
with col1: st.title("🅿️ Parking Slot Booking")
with col2:
    if st.button("Logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
if 'vehicle_number' not in st.session_state or st.session_state.vehicle_number is None:
    v = st.text_input("Enter Vehicle Number (one time requirement)")
    if st.button("Save Vehicle Number", type="primary"):
        cur.execute("UPDATE users SET vehicle_number=? WHERE id=?", (v.upper(), st.session_state.user_id)); conn.commit(); st.session_state.vehicle_number = v.upper(); st.rerun()
    st.stop()

st.header("Dashboard Overview")
col1, col2 = st.columns(2)
with col1:
    now_dt = datetime.now()
    active = cur.execute("SELECT slot_number, end_datetime FROM bookings WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))).fetchone()
    if active:
        end_time = datetime.strptime(active[1], "%Y-%m-%d %H:%M")
        st.success(f"**Currently Parked**\n\n**Slot:** {active[0]}\n\n**Until:** {end_time.strftime('%I:%M %p')}\n\n**Time Remaining:** {str(end_time - now_dt).split('.')[0]}")
    else: st.info("No active parking session.")
with col2: st.metric("Total Lifetime Bookings", cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0])

st.header("Book a New Parking Slot")
st.markdown("<p style='color: var(--color-text-secondary);'>Step 1: Select your desired time frame.</p>", unsafe_allow_html=True)
booking_date = st.date_input("Select Date", min_value=date.today())
col1, col2 = st.columns(2)
with col1: entry_time = st.time_input("Select Entry Time", value=datetime.now().replace(second=0, microsecond=0).time())
with col2: exit_time = st.time_input("Select Exit Time")

start_dt, end_dt = datetime.combine(booking_date, entry_time), datetime.combine(booking_date, exit_time)
if exit_time <= entry_time:
    end_dt += timedelta(days=1)
    st.warning("Exit time is before entry. Booking will extend to the next day.", icon="⚠️")

# --- CLICKABLE LIVE AVAILABILITY GRID (The Correct Way) ---
st.markdown("<p style='color: var(--color-text-secondary);'>Step 2: Click an available slot below.</p>", unsafe_allow_html=True)
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]
blocked_for_selection = {r[0] for r in cur.execute("SELECT slot_number FROM bookings WHERE NOT (end_datetime <=? OR start_datetime >=?)", (start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))).fetchall()}

def handle_slot_click(slot_name):
    if st.session_state.selected_slot == slot_name: st.session_state.selected_slot = None
    else: st.session_state.selected_slot = slot_name

# --- Inject CSS for slot colors dynamically ---
slot_styles = ""
for s in slots:
    is_blocked = s in blocked_for_selection
    is_selected = s == st.session_state.selected_slot
    
    # Base selector for this specific button
    selector = f'button[data-testid*="st.button"][data-testid$="slot_{s}"]'

    if is_selected:
        slot_styles += f"{selector} {{ border: 2px solid var(--color-accent); background-color: rgba(74, 144, 226, 0.1); color: white!important; }}\n"
    elif is_blocked:
        slot_styles += f"{selector} {{ border-left: 3px solid var(--color-busy); color: var(--color-text-secondary); }}\n"
    else: # Free
        slot_styles += f"{selector} {{ border-left: 3px solid var(--color-free); color: var(--color-free); }}\n"

st.markdown(f"<style>{slot_styles}</style>", unsafe_allow_html=True)

# Display the grid
num_columns = 10
rows = [slots[i:i + num_columns] for i in range(0, len(slots), num_columns)]
for row in rows:
    cols = st.columns(num_columns)
    for i, s in enumerate(row):
        with cols[i]:
            is_blocked = s in blocked_for_selection
            st.button(s, key=f"slot_{s}", on_click=handle_slot_click, args=(s,), disabled=is_blocked, use_container_width=True)

# --- CONFIRMATION SECTION ---
if st.session_state.selected_slot:
    if st.session_state.selected_slot in blocked_for_selection:
        st.error(f"Slot {st.session_state.selected_slot} is no longer available.", icon="🚫")
        st.session_state.selected_slot = None
        st.rerun()
    else:
        st.info(f"You have selected slot **{st.session_state.selected_slot}**. Please confirm your booking.", icon="🅿️")
        if st.button("Confirm Booking", type="primary", use_container_width=True):
            if cur.execute("SELECT id FROM bookings WHERE user_id=? AND NOT (end_datetime <=? OR start_datetime >=?)", (st.session_state.user_id, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))).fetchone():
                st.error("You already have an overlapping booking.", icon="🚫")
            else:
                cur.execute("INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)", (st.session_state.user_id, st.session_state.selected_slot, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Slot {st.session_state.selected_slot} booked successfully!", icon="✅")
                st.session_state.selected_slot = None
                st.rerun()
else:
    st.warning("No slot selected. Please choose a time and click an available slot.", icon="👆")
