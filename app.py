import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

# ---------- AUTO REFRESH (1 SECOND) ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- UPDATED UI STYLESHEET FOR MOBILE RESPONSIVENESS ----------
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
    color: var(--color-text-primary); /* Ensure base text color */
}

/* --- Typography --- */
h1, h2, h3 { color: var(--color-text-primary); font-family: var(--font-family); letter-spacing: -0.02em; }
h1 { font-weight: 600; font-size: 1.75rem; padding-bottom: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--color-border); }
h2 { font-weight: 500; font-size: 1.25rem; color: var(--color-text-secondary); margin-top: 2.5rem; margin-bottom: 1rem; }
h3 { font-weight: 500; font-size: 1.1rem; margin-top: 2rem; margin-bottom: 0.5rem; }

/* --- Standard UI Elements --- */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stSelectbox > div > div > div > div { /* Target selectbox as well */
    background-color: var(--color-bg);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    transition: all 0.2s ease;
    padding: 0.75rem 1rem; /* More comfortable padding */
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTimeInput > div > div > input:focus,
.stSelectbox > div > div > div > div:focus-within {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
    outline: none;
}
.stButton > button.primary { 
    background-color: var(--color-accent); 
    border-color: var(--color-accent); 
    color: #FFFFFF; 
    padding: 0.75rem 1.25rem; /* Better button padding */
    font-size: 1rem; /* Readable button text */
    height: auto; /* Allow height to adjust */
}
.stButton > button.primary:hover { 
    background-color: #5A9EE8; 
    border-color: #5A9EE8; 
}
/* General button styling for better touch targets */
.stButton button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    min-height: 44px; /* Ensure minimum touch target size */
}

/* --- Card Styling --- */
div[data-testid="stMetric"], div[data-testid="stAlert"] {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    height: 100%;
}
div[data-testid="stAlert"][data-baseweb="alert-success"] { background-color: rgba(34, 129, 74, 0.1); border-color: rgba(34, 129, 74, 0.3); color: var(--color-free); }
div[data-testid="stAlert"][data-baseweb="alert-info"] { background-color: rgba(74, 144, 226, 0.1); border-color: rgba(74, 144, 226, 0.3); color: var(--color-accent); }
div[data-testid="stAlert"][data-baseweb="alert-warning"] { background-color: rgba(255, 193, 7, 0.1); border-color: rgba(255, 193, 7, 0.3); color: #FFC107; }
div[data-testid="stAlert"][data-baseweb="alert-error"] { background-color: rgba(220, 53, 69, 0.1); border-color: rgba(220, 53, 69, 0.3); color: var(--color-busy); }

/* --- Styling for st.button used as slots --- */
div[data-testid="stHorizontalBlock"] {
    gap: 0.75rem;
    flex-wrap: wrap; /* Allow slots to wrap on smaller screens */
}
.stButton button {
    width: 100%; /* Default to full width for small screens */
    height: 60px; /* Adjusted height */
    padding: 0;
    margin: 0;
    font-size: 1.1rem; /* Larger slot number */
    font-weight: 600;
    background-color: var(--color-bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.2s ease;
    flex-grow: 1; /* Allow buttons to grow */
    flex-shrink: 0; /* Prevent shrinking too much */
    flex-basis: calc(20% - 0.75rem); /* Default 5 per row for wider mobile views */
    min-width: 80px; /* Minimum width for slot button */
}

/* Specific styling for column layout of slots */
.stHorizontalBlock {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px; /* Consistent gap */
    justify-content: flex-start;
}
.stHorizontalBlock > div {
    flex: 1 1 auto; /* Each column item can grow/shrink */
    min-width: 80px; /* Ensure readability */
    max-width: 18%; /* Roughly 5 per row for decent screen sizes */
    box-sizing: border-box; /* Include padding/border in width */
}
.stHorizontalBlock > div >.stButton {
    height: 100%;
}

.stHorizontalBlock > div >.stButton > button {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* --- Mobile-specific adjustments --- */
@media (max-width: 768px) { /* Tablets and smaller */
    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.1rem; }
    h3 { font-size: 1rem; }

    /* Adjust padding and font size for inputs on mobile */
  .stTextInput > div > div > input,
  .stDateInput > div > div > input,
  .stTimeInput > div > div > input,
  .stSelectbox > div > div > div > div {
        padding: 0.6rem 0.8rem;
        font-size: 0.95rem;
    }

    /* Smaller padding for cards */
    div[data-testid="stMetric"], div[data-testid="stAlert"] {
        padding: 1rem;
    }

    /* Make columns stack on small screens for better readability */
  .stApp > div > div:nth-child(1) > div:nth-child(2) > div, /* Targeting top level columns */
  .stApp > div > div:nth-child(1) > div:nth-child(3) > div { /* Targeting dashboard columns */
        flex-direction: column;
        gap: 1rem;
    }

    /* Full width buttons for primary actions */
  .stButton > button.primary {
        width: 100%;
    }

    /* Slot grid adjustments for mobile */
  .stHorizontalBlock > div {
        flex-basis: calc(33.333% - 0.75rem); /* 3 slots per row */
        max-width: calc(33.333% - 0.75rem);
    }
  .stHorizontalBlock > div:nth-child(3n) { /* Adjust for last item in row */
        margin-right: 0;
    }
}

@media (max-width: 480px) { /* Extra small screens / most phones */
    h1 { font-size: 1.3rem; margin-bottom: 1rem; }
    h2 { margin-top: 1.5rem; margin-bottom: 0.8rem; }

  .stButton button {
        height: 50px; /* Slightly smaller height for very small screens */
        font-size: 1rem;
    }

    /* Even fewer slots per row for tiny screens */
  .stHorizontalBlock > div {
        flex-basis: calc(50% - 0.75rem); /* 2 slots per row */
        max-width: calc(50% - 0.75rem);
    }
  .stHorizontalBlock > div:nth-child(2n) { /* Adjust for last item in row */
        margin-right: 0;
    }
}
</style>
""", unsafe_allow_html=True)

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
    active_booking_query = cur.execute("SELECT id, slot_number, end_datetime FROM bookings WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))).fetchone()
    if active_booking_query:
        active_booking_id, slot_num, end_time_str = active_booking_query
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        st.success(f"**Currently Parked**\n\n**Slot:** {slot_num}\n\n**Until:** {end_time.strftime('%I:%M %p')}\n\n**Time Remaining:** {str(end_time - now_dt).split('.')[0]}")
    else: 
        st.info("No active parking session.")
        active_booking_id = None # Ensure active_booking_id is None if no active booking

with col2: st.metric("Total Lifetime Bookings", cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id=?", (st.session_state.user_id,)).fetchone()[0]) # Changed to count user's bookings

# --- CANCEL/END BOOKING SECTION ---
st.subheader("Manage Your Bookings")
user_bookings = cur.execute("SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? ORDER BY start_datetime", (st.session_state.user_id,)).fetchall()

if user_bookings:
    for booking_id, slot_number, start_dt_str, end_dt_str in user_bookings:
        start_dt_obj = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
        end_dt_obj = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M")
        
        is_active = (start_dt_obj <= now_dt <= end_dt_obj)
        is_future = (start_dt_obj > now_dt)
        is_past = (end_dt_obj < now_dt)

        if is_active:
            status_text = "Active Now"
            button_label = "End Session Early"
            button_key = f"end_booking_{booking_id}"
            button_help = "Ends your current parking session immediately."
            button_color = "secondary" # Make it a standard button color
        elif is_future:
            status_text = "Upcoming"
            button_label = "Cancel Booking"
            button_key = f"cancel_booking_{booking_id}"
            button_help = "Cancels this future booking."
            button_color = "secondary"
        else: # Past booking
            status_text = "Completed"
            button_label = "Booking History" # No action needed
            button_key = f"view_history_{booking_id}"
            button_color = "disabled" # Visually disable

        booking_col1, booking_col2, booking_col3 = st.columns([0.5, 3, 2])
        with booking_col1:
            st.markdown(f"**{slot_number}**")
        with booking_col2:
            st.markdown(f"*{status_text}* from {start_dt_obj.strftime('%Y-%m-%d %I:%M %p')} to {end_dt_obj.strftime('%Y-%m-%d %I:%M %p')}")
        with booking_col3:
            if button_color!= "disabled":
                if st.button(button_label, key=button_key, type=button_color, help=button_help):
                    if st.session_state[f"confirm_{button_key}"] if f"confirm_{button_key}" in st.session_state else False:
                        # User confirmed, proceed with deletion
                        cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                        conn.commit()
                        st.success(f"{'Session ended' if is_active else 'Booking cancelled'} for slot {slot_number}.")
                        del st.session_state[f"confirm_{button_key}"] # Clear confirmation state
                        st.rerun()
                    else:
                        # First click, ask for confirmation
                        st.session_state[f"confirm_{button_key}"] = True
                        st.warning("Click again to confirm!", icon="⚠️")
            else:
                st.button(button_label, key=button_key, disabled=True)

else:
    st.info("You have no current or upcoming bookings.")

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
# Use st.columns to create a flexible grid that wraps
num_columns_desktop = 10
# For mobile, we'll aim for fewer columns (e.g., 3 or 2)
# The CSS media queries handle this by adjusting flex-basis
for i in range(0, len(slots), num_columns_desktop):
    row_slots = slots[i:i + num_columns_desktop]
    cols = st.columns(len(row_slots)) # Create columns dynamically based on row length
    for j, s in enumerate(row_slots):
        with cols[j]:
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
            # Check for overlapping bookings for *this user*, excluding current active session if it exists and is not the one being rebooked
            # If a user ends a session, they should be able to book immediately again if the slot is free.
            # This logic implicitly handles that by checking *all* bookings against new dates
            overlapping_query = cur.execute("SELECT id FROM bookings WHERE user_id=? AND NOT (end_datetime <=? OR start_datetime >=?)", (st.session_state.user_id, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))).fetchone()

            if overlapping_query:
                st.error("You already have an overlapping booking. Please cancel it first.", icon="🚫")
            else:
                cur.execute("INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)", (st.session_state.user_id, st.session_state.selected_slot, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Slot {st.session_state.selected_slot} booked successfully!", icon="✅")
                st.session_state.selected_slot = None
                st.rerun()
else:
    st.warning("No slot selected. Please choose a time and click an available slot.", icon="👆")
