import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

# ---------- AUTO REFRESH (1 SECOND) ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- "15 YEARS OF EXPERIENCE" UI STYLESHEET ----------
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
    --color-accent: #4A90E2;
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
.stButton > button {
    font-weight: 500;
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    transition: background-color 0.15s ease-in-out;
}
.stButton > button:hover { background-color: #242424; }
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

/* --- Clickable Slot Grid Styling --- */
.slot-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 0.75rem; margin-top: 1rem; margin-bottom: 2rem; }
.slot-link { text-decoration: none; }
.slot {
    padding: 1rem 0;
    text-align: center;
    border-radius: var(--border-radius);
    font-weight: 500;
    color: var(--color-text-primary);
    background-color: #242424;
    border: 1px solid var(--color-border);
    transition: border-color 0.2s ease;
}
.slot.clickable:hover { border-color: var(--color-text-secondary); cursor: pointer; }
.slot.free { color: #50A86E; border-left: 3px solid #50A86E; }
.slot.busy { color: #B9535A; border-left: 3px solid #B9535A; background-color: #1A1A1A; }
.slot.yours { color: #A0A0A0; border-left: 3px solid #A0A0A0; }
.slot.selected {
    border: 2px solid var(--color-accent)!important;
    background-color: rgba(74, 144, 226, 0.1);
}
.slot small { font-weight: 400; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-secondary); }

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
# Use query params to set the selected slot
selected_slot_from_query = st.query_params.get("slot")
if "selected_slot" not in st.session_state:
    st.session_state.selected_slot = selected_slot_from_query
elif selected_slot_from_query:
    if st.session_state.selected_slot == selected_slot_from_query:
         st.session_state.selected_slot = None # Toggle off
    else:
         st.session_state.selected_slot = selected_slot_from_query
    st.query_params.clear()

# ---------- AUTH PAGE (BUG FIX) ----------
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

# --- CLICKABLE LIVE AVAILABILITY GRID (Using HTML for visuals) ---
st.markdown("<p style='color: var(--color-text-secondary);'>Step 2: Click an available slot below.</p>", unsafe_allow_html=True)
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]
blocked_for_selection = {r[0] for r in cur.execute("SELECT slot_number FROM bookings WHERE NOT (end_datetime <=? OR start_datetime >=?)", (start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))).fetchall()}
my_active_slot = next((s[0] for s in cur.execute("SELECT slot_number FROM bookings WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime", (st.session_state.user_id, datetime.now().strftime("%Y-%m-%d %H:%M")))), None)

grid_html = "<div class='slot-grid'>"
for s in slots:
    is_blocked = s in blocked_for_selection
    is_selected = s == st.session_state.selected_slot
    is_mine_now = s == my_active_slot

    # Determine class and label
    if is_mine_now:
        label, status_class = "YOURS", "yours"
    elif is_blocked:
        label, status_class = "BUSY", "busy"
    else:
        label, status_class = "FREE", "free clickable"

    if is_selected and not is_blocked:
        status_class += " selected"

    # Build the HTML for the slot
    slot_div = f"<div class='slot {status_class}'>{s}<br><small>{label}</small></div>"
    
    # If the slot is not blocked, wrap it in a clickable link
    if not is_blocked:
        grid_html += f"<a href='?slot={s}' class='slot-link'>{slot_div}</a>"
    else:
        grid_html += slot_div

grid_html += "</div>"
st.markdown(grid_html, unsafe_allow_html=True)

# --- CONFIRMATION SECTION ---
if st.session_state.selected_slot:
    if st.session_state.selected_slot in blocked_for_selection:
        st.error(f"Slot {st.session_state.selected_slot} is no longer available. The grid has updated.", icon="🚫")
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
