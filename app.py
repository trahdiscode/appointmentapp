import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

# ---------- AUTO REFRESH (1 SECOND) ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- UPDATED UI STYLESHEET FOR MOBILE RESPONSIVENESS AND VISUAL APPEAL ----------
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
    --spacing-unit: 1.5rem; /* Base spacing unit */
}

/* --- Base App Styling --- */
.stApp {
    background-color: var(--color-bg);
    font-family: var(--font-family);
    color: var(--color-text-primary); /* Ensure base text color */
    padding: 0; /* Remove default app padding to control it via main block-container */
}
.main.block-container {
    padding-top: var(--spacing-unit);
    padding-right: var(--spacing-unit);
    padding-left: var(--spacing-unit);
    padding-bottom: var(--spacing-unit);
}

/* --- Typography --- */
h1, h2, h3 { color: var(--color-text-primary); font-family: var(--font-family); letter-spacing: -0.02em; }
h1 { 
    font-weight: 600; 
    font-size: 2rem; /* Slightly larger for impact */
    padding-bottom: 0.5rem; 
    margin-bottom: var(--spacing-unit); 
    border-bottom: 1px solid var(--color-border); 
}
h2 { 
    font-weight: 500; 
    font-size: 1.5rem; /* Adjusted for better hierarchy */
    color: var(--color-text-primary); /* Main headers primary color */
    margin-top: calc(2 * var(--spacing-unit)); /* More space above major sections */
    margin-bottom: 1rem; 
}
h3 { 
    font-weight: 500; 
    font-size: 1.2rem; /* Adjusted */
    color: var(--color-text-secondary); 
    margin-top: var(--spacing-unit); 
    margin-bottom: 0.5rem; 
}
h4 { /* Added for sub-sections like Past Bookings */
    font-weight: 500;
    font-size: 1.1rem;
    color: var(--color-text-primary);
    margin-top: var(--spacing-unit);
    margin-bottom: 0.75rem;
}

/* --- Standard UI Elements --- */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stSelectbox > div > div > div > div { /* Target selectbox as well */
    background-color: var(--color-bg-secondary); /* Input background matching cards */
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
    border-radius: var(--border-radius); /* Consistent border-radius */
}
.stButton > button.primary:hover { 
    background-color: #5A9EE8; 
    border-color: #5A9EE8; 
}

/* Secondary button styling for actions like cancel/end */
.stButton > button.secondary {
    background-color: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
    border-radius: var(--border-radius);
    transition: all 0.2s ease;
}
.stButton > button.secondary:hover:not(:disabled) {
    background-color: var(--color-bg-secondary);
    border-color: var(--color-accent);
    color: var(--color-text-primary);
}

/* General button styling for better touch targets */
.stButton button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    min-height: 44px; /* Ensure minimum touch target size */
    border-radius: var(--border-radius); /* Consistent border-radius */
}

/* --- Card Styling (stMetric, stAlert) --- */
div[data-testid="stMetric"], div[data-testid="stAlert"] {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: var(--spacing-unit); /* Consistent padding */
    height: 100%;
    margin-bottom: var(--spacing-unit); /* Spacing below cards */
}
div[data-testid="stAlert"] { /* Alerts should visually stand out */
    padding: 1rem 1.25rem;
    border-left: 5px solid; /* Stronger border for alerts */
    background-color: var(--color-bg); /* Use base bg for alerts */
}

div[data-testid="stAlert"][data-baseweb="alert-success"] { border-color: var(--color-free); background-color: rgba(34, 129, 74, 0.1); color: var(--color-free); }
div[data-testid="stAlert"][data-baseweb="alert-info"] { border-color: var(--color-accent); background-color: rgba(74, 144, 226, 0.1); color: var(--color-accent); }
div[data-testid="stAlert"][data-baseweb="alert-warning"] { border-color: #FFC107; background-color: rgba(255, 193, 7, 0.1); color: #FFC107; }
div[data-testid="stAlert"][data-baseweb="alert-error"] { border-color: var(--color-busy); background-color: rgba(220, 53, 69, 0.1); color: var(--color-busy); }

/* Customizing stMetric for dashboard */
div[data-testid="stMetric"] label { /* Metric label */
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    /* --- FIX FOR TRUNCATED METRIC LABEL --- */
    white-space: normal!important; /* Force text wrapping */
    overflow: visible!important; /* Ensure content is not clipped */
    text-overflow: unset!important; /* Remove ellipsis */
    width: 100%!important; /* Take full available width */
    display: block!important; /* Ensure it's a block element for proper layout */
}
div[data-testid="stMetric"] div[data-testid="stMarkdownContainer"] p { /* Metric value */
    color: var(--color-text-primary);
    font-size: 2.5rem; /* Larger metric values */
    font-weight: 700;
    line-height: 1;
}

/* Customizing the 'Currently Parked' success alert for metric-like display */
.stAlert.stAlert--success {
    background-color: var(--color-bg-secondary); /* Darker background for active parking */
    border-left-color: var(--color-free);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: var(--spacing-unit);
    color: var(--color-free);
    margin-bottom: var(--spacing-unit); /* Add spacing */
}
.stAlert.stAlert--success.stMarkdownContainer p {
    color: var(--color-text-primary); /* General text in active parking card */
}
.stAlert.stAlert--success.stMarkdownContainer strong {
    color: var(--color-free); /* Highlighted text in active parking card */
}
/* Adjusting success alert specific text for better readability */
.stAlert.stAlert--success.stMarkdownContainer strong:first-child { /* "Currently Parked" */
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    display: block;
    color: var(--color-free);
}
.stAlert.stAlert--success.stMarkdownContainer strong:nth-child(2) { /* "Slot: B5" */
    font-size: 1.5rem;
    margin-top: 0.5rem;
    display: block;
    color: var(--color-text-primary);
}
.stAlert.stAlert--success.stMarkdownContainer strong:nth-child(3) { /* "Until: 05:00 PM" */
    font-size: 1.1rem;
    display: block;
    color: var(--color-text-secondary);
}
.stAlert.stAlert--success.stMarkdownContainer strong:last-child { /* "Time Remaining: 0:39:08" */
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 0.75rem;
    display: block;
    color: var(--color-free);
}

/* --- Styling for st.button used as slots --- */
div[data-testid="stHorizontalBlock"] {
    gap: 0.75rem;
    flex-wrap: wrap; /* Allow slots to wrap on smaller screens */
    margin-bottom: var(--spacing-unit); /* Add spacing below the grid */
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

/* Manage bookings item styling */
.manage-booking-item {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: 1rem;
    margin-bottom: 0.75rem; /* Spacing between booking items */
    display: flex;
    align-items: center;
    gap: 1rem;
}
.manage-booking-item > div:first-child { /* Slot number */
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--color-text-primary);
    min-width: 40px; /* Ensure space for slot like B5 */
}
.manage-booking-item > div:nth-child(2) { /* Details */
    flex-grow: 1;
    color: var(--color-text-secondary);
}
.manage-booking-item > div:nth-child(2) > * { /* ensure children take up available space */
    color: var(--color-text-secondary);
}
.manage-booking-item > div:last-child { /* Button column */
    min-width: 120px; /* Ensure button fits */
    text-align: right;
}

/* Separator styling */
hr {
    border-top: 1px solid var(--color-border);
    margin-top: calc(1.5 * var(--spacing-unit));
    margin-bottom: calc(1.5 * var(--spacing-unit));
}

/* Custom styling for the main title and logout button alignment */
/* This targets the div that contains your main Streamlit content */
.st-emotion-cache-18ni7ap.e1fqkh3o5 {
    width: 100%;
}
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem; /* Add some padding below the header area */
    border-bottom: 1px solid var(--color-border);
    margin-bottom: var(--spacing-unit); /* Space below the main header line */
}
.header-title {
    font-weight: 600;
    font-size: 2rem;
    color: var(--color-text-primary);
    margin: 0; /* Remove default margin */
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.header-title.emoji {
    font-size: 2rem; /* Keep emoji size consistent with title */
}
/* Adjust the logout button inside the header */
.header-container.stButton > button {
    margin-left: auto; /* Push the button to the right */
    min-width: unset; /* Allow button to shrink if needed */
    padding: 0.5rem 1rem; /* Adjust padding for better look */
}

/* --- Mobile-specific adjustments --- */
@media (max-width: 768px) { /* Tablets and smaller */
.stApp {
        padding: 1rem; /* Less overall padding on mobile */
    }
.main.block-container {
        padding: 1rem;
    }
    h1 { font-size: 1.5rem; margin-bottom: 1rem; }
    h2 { font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.8rem; }
    h3 { font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem; }
    h4 { font-size: 1rem; margin-top: 1rem; margin-bottom: 0.6rem; }

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
        margin-bottom: 1rem;
    }

    /* Full width primary buttons */
.stButton > button.primary {
        width: 100%;
        font-size: 0.95rem;
        padding: 0.6rem 1rem;
    }
    /* Secondary buttons should also adapt */
.stButton > button.secondary {
        width: 100%;
        font-size: 0.85rem;
        padding: 0.5rem 0.8rem;
    }

    /* Slot grid adjustments for mobile */
.stHorizontalBlock > div {
        flex-basis: calc(33.333% - 0.75rem); /* 3 slots per row */
        max-width: calc(33.333% - 0.75rem);
    }
.stHorizontalBlock > div:nth-child(3n) { /* Adjust for last item in row */
        margin-right: 0;
    }

    /* Manage booking item columns to stack */
.manage-booking-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.75rem;
    }
.manage-booking-item > div:first-child {
        min-width: unset;
        width: 100%;
    }
.manage-booking-item > div:nth-child(2) {
        width: 100%;
    }
.manage-booking-item > div:last-child {
        width: 100%;
        text-align: left;
    }
.header-container { /* Ensure header container also adapts */
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }
.header-title {
        width: 100%; /* Make title take full width */
        font-size: 1.8rem;
    }
    /* Adjust the logout button inside the mobile header */
   .header-container.stButton > button {
        margin-left: unset; /* Remove auto margin on mobile */
        width: 100%; /* Make it full width */
    }
}

@media (max-width: 480px) { /* Extra small screens / most phones */
    h1 { font-size: 1.3rem; margin-bottom: 0.75rem; }
    h2 { margin-top: 1rem; margin-bottom: 0.6rem; }

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
.header-title {
        font-size: 1.5rem;
    }
.header-title.emoji {
        font-size: 1.5rem;
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

# Custom header for title and logout button
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<div class="header-title"><span class="emoji">🅿️</span> Parking Slot Booking</div>', unsafe_allow_html=True)
if st.button("Logout", type="secondary"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Moved the horizontal line from st.title to the custom header
# and removed the st.title which has the default line

if 'vehicle_number' not in st.session_state or st.session_state.vehicle_number is None:
    st.info("Please enter your vehicle number to proceed. This is a one-time requirement.", icon="🚗")
    v = st.text_input("Enter Vehicle Number", placeholder="e.g., TN01 AB1234") # Added placeholder
    if st.button("Save Vehicle Number", type="primary", use_container_width=True):
        if v.strip() == "":
            st.error("Vehicle number cannot be empty.")
        else:
            cur.execute("UPDATE users SET vehicle_number=? WHERE id=?", (v.upper(), st.session_state.user_id)); conn.commit(); st.session_state.vehicle_number = v.upper(); st.rerun()
    st.stop()

st.subheader("Dashboard Overview") # Changed to subheader for consistent hierarchy
col1, col2 = st.columns(2)
now_dt = datetime.now()
user_has_active_or_future_booking = False
# Query for current and future bookings
user_current_future_bookings = cur.execute("SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? AND end_datetime >? ORDER BY start_datetime", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))).fetchall()

if user_current_future_bookings:
    user_has_active_or_future_booking = True
    # Filter for active booking to display in the dashboard metric
    active_booking_query = next((booking for booking in user_current_future_bookings if datetime.strptime(booking[2], "%Y-%m-%d %H:%M") <= now_dt <= datetime.strptime(booking[3], "%Y-%m-%d %H:%M")), None)
else:
    active_booking_query = None

with col1:
    if active_booking_query:
        active_booking_id, slot_num, start_time_str, end_time_str = active_booking_query
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        # Custom display for active parking to fit the design
        st.success(f"""
        **Currently Parked**

        **Slot:** {slot_num}

        **Until:** {end_time.strftime('%I:%M %p')}

        **Time Remaining:** {str(end_time - now_dt).split('.')[0]}
        """, icon="🚗") # Changed icon to car for active parking
    else: 
        st.info("No active parking session.", icon="💤") # Sleepy icon for no active session

with col2: st.metric("Total Lifetime Bookings", cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id=?", (st.session_state.user_id,)).fetchone()[0])

# --- MANAGE BOOKINGS SECTION ---
st.subheader("Manage Your Bookings")

if user_current_future_bookings: # Display current/future bookings here
    for booking_id, slot_number, start_dt_str, end_dt_str in user_current_future_bookings:
        start_dt_obj = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
        end_dt_obj = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M")
        
        is_active = (start_dt_obj <= now_dt <= end_dt_obj)
        is_future = (start_dt_obj > now_dt)

        if is_active:
            status_text = "Active Now"
            button_label = "End Session Early"
            button_key = f"end_booking_{booking_id}"
            button_help = "Ends your current parking session immediately."
            button_type = "secondary" 
        elif is_future:
            status_text = "Upcoming"
            button_label = "Cancel Booking"
            button_key = f"cancel_booking_{booking_id}"
            button_help = "Cancels this future booking."
            button_type = "secondary"
        
        # Use a custom div for each booking item to control layout and styling
        st.markdown(f"""
        <div class="manage-booking-item">
            <div>{slot_number}</div>
            <div>
                <p><i>{status_text}</i></p>
                <p>{start_dt_obj.strftime('%Y-%m-%d %I:%M %p')} to {end_dt_obj.strftime('%Y-%m-%d %I:%M %p')}</p>
            </div>
            <div>
        """, unsafe_allow_html=True)
        # Place button inside the HTML div
        if st.button(button_label, key=button_key, type=button_type, help=button_help):
            if st.session_state.get(f"confirm_{button_key}", False):
                cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                conn.commit()
                st.success(f"{'Session ended' if is_active else 'Booking cancelled'} for slot {slot_number}.", icon="✅")
                del st.session_state[f"confirm_{button_key}"] # Clear confirmation state
                st.session_state.selected_slot = None # Clear any pending selection
                st.rerun()
            else:
                st.session_state[f"confirm_{button_key}"] = True
                st.warning("Click again to confirm!", icon="⚠️")
        st.markdown("</div></div>", unsafe_allow_html=True) # Close the HTML div
else: # No current or future bookings
    st.info("You have no current or upcoming bookings.", icon="🗓️")

# Display past bookings
past_bookings = cur.execute("SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? AND end_datetime <=? ORDER BY start_datetime DESC", (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))).fetchall()
if past_bookings:
    st.markdown("---") # Visual separator
    st.subheader("Booking History") # Changed to subheader
    for booking_id, slot_number, start_dt_str, end_dt_str in past_bookings:
        start_dt_obj = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
        end_dt_obj = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M")
        # Simplified display for past bookings
        st.markdown(f"<div class='manage-booking-item'><div style='color: var(--color-text-secondary);'>{slot_number}</div><div><p><i>Completed</i></p><p>{start_dt_obj.strftime('%Y-%m-%d %I:%M %p')} to {end_dt_obj.strftime('%Y-%m-%d %I:%M %p')}</p></div><div></div></div>", unsafe_allow_html=True)

st.markdown("---") # Separator between sections

# --- Book a New Parking Slot Section (Conditional Display) ---
if not user_has_active_or_future_booking: # Only show if no active/future bookings
    st.subheader("Book a New Parking Slot")
    st.markdown("<p style='color: var(--color-text-secondary);'>Step 1: Select your desired time frame.</p>", unsafe_allow_html=True)
    
    # Use columns for date/time inputs for better alignment on web
    col_date, col_entry_time, col_exit_time = st.columns(3)
    with col_date:
        booking_date = st.date_input("Select Date", min_value=date.today(), key="booking_date_input")
    with col_entry_time: 
        entry_time = st.time_input("Select Entry Time", value=datetime.now().replace(second=0, microsecond=0).time(), key="entry_time_input")
    with col_exit_time: 
        exit_time = st.time_input("Select Exit Time", key="exit_time_input")

    start_dt, end_dt = datetime.combine(booking_date, entry_time), datetime.combine(booking_date, exit_time)
    if exit_time <= entry_time:
        end_dt += timedelta(days=1)
        st.warning("Exit time is before entry. Booking will extend to the next day.", icon="⚠️")

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
        
        selector = f'button[data-testid*="st.button"][data-testid$="slot_{s}"]'

        if is_selected:
            slot_styles += f"{selector} {{ border: 2px solid var(--color-accent); background-color: rgba(74, 144, 226, 0.1); color: white!important; }}\n"
        elif is_blocked:
            slot_styles += f"{selector} {{ border-left: 3px solid var(--color-busy); color: var(--color-text-secondary); }}\n"
        else: # Free
            slot_styles += f"{selector} {{ border-left: 3px solid var(--color-free); color: var(--color-free); }}\n"

    st.markdown(f"<style>{slot_styles}</style>", unsafe_allow_html=True)

    # Display the grid
    num_columns_desktop = 10
    for i in range(0, len(slots), num_columns_desktop):
        row_slots = slots[i:i + num_columns_desktop]
        cols = st.columns(len(row_slots))
        for j, s in enumerate(row_slots):
            with cols[j]:
                is_blocked = s in blocked_for_selection
                is_disabled = is_blocked or (st.session_state.selected_slot is not None and st.session_state.selected_slot!= s)
                
                st.button(s, key=f"slot_{s}", on_click=handle_slot_click, args=(s,), disabled=is_disabled, use_container_width=True)

    # --- CONFIRMATION SECTION ---
    if st.session_state.selected_slot:
        if st.session_state.selected_slot in blocked_for_selection:
            st.error(f"Slot {st.session_state.selected_slot} is no longer available.", icon="🚫")
            st.session_state.selected_slot = None
            st.rerun()
        else:
            st.info(f"You have selected slot **{st.session_state.selected_slot}**. Please confirm your booking.", icon="🅿️")
            if st.button("Confirm Booking", type="primary", use_container_width=True):
                cur.execute("INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)", (st.session_state.user_id, st.session_state.selected_slot, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Slot {st.session_state.selected_slot} booked successfully!", icon="✅")
                st.session_state.selected_slot = None
                st.rerun()
    else:
        st.warning("No slot selected. Please choose a time and click an available slot.", icon="👆")
else:
    st.info("You already have an active or upcoming parking session. Please manage existing bookings first to book a new slot.", icon="ℹ️")
