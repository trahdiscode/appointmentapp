import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Parking Slot Booking", layout="wide")

from streamlit_autorefresh import st_autorefresh
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ---------- AUTO REFRESH ----------
# st_autorefresh(interval=5000, key="refresh") # Commenting out for cleaner testing, uncomment if needed

# ---------- DARK MODE CSS (Revised with distinct fonts and colors) ----------
st.markdown("""
<style>
/* Overall App Styling - Using a cleaner, modern sans-serif font */
.stApp {
    background-color: #0f1117; /* Dark background */
    color: #f0f2f6; /* Light text for contrast */
    font-family: 'Open Sans', 'Segoe UI', 'Roboto', sans-serif; /* Modern, clean font stack */
    line-height: 1.6;
}

/* Headings */
/* Main title - for 'Parking Slot Booking' (e.g., in st.title) */
h1.css-1r6dm7m { /* Target Streamlit's generated <h1> */
    font-family: 'Playfair Display', serif; /* A distinctive, elegant serif font */
    font-size: 3.2em; /* Significantly larger */
    color: #bdbdbd; /* A professional light grey */
    font-weight: 700; /* Bold and impactful */
    border-bottom: 3px solid #4a4a4a; /* A thicker, dark grey border */
    padding-bottom: 18px; /* More space above border */
    margin-bottom: 40px; /* More space below title */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.4); /* Subtle text shadow */
}

/* Dashboard title - for 'Parking Dashboard' (e.g., in st.header) */
h2.css-10trblm { /* Target Streamlit's generated <h2> */
    font-family: 'Montserrat', sans-serif; /* A strong, clean sans-serif font */
    font-size: 2.2em; /* Distinct, yet not as dominant as main title */
    color: #8bbdc2; /* A professional bluish-grey */
    font-weight: 600; /* Medium bold */
    border-bottom: 1px solid #5a5a5a; /* Lighter border */
    padding-bottom: 12px;
    margin-top: 50px; /* More space before section */
    margin-bottom: 30px;
}

/* Subheadings (e.g., in st.subheader) */
h3.css-10trblm { /* Target Streamlit's generated <h3> */
    font-family: 'Open Sans', sans-serif; /* Consistent with body text, but distinct size */
    font-size: 1.6em;
    color: #e0e0e0; /* Brighter for sub-sections */
    margin-top: 35px;
    margin-bottom: 18px;
    font-weight: 500;
}

/* Input Fields */
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stSelectbox > div > div > button {
    background-color: #161b22; /* Darker input background */
    color: #f0f2f6;
    border: 1px solid #30363d; /* Subtle border */
    border-radius: 5px;
    padding: 10px 12px;
    font-family: 'Open Sans', sans-serif; /* Consistent font */
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTimeInput > div > div > input:focus,
.stSelectbox > div > div > button:focus {
    border-color: #58a6ff; /* Highlight on focus */
    box-shadow: 0 0 0 0.1rem rgba(88, 166, 255, 0.25);
}

/* Buttons */
.stButton > button {
    background-color: #21262d; /* Dark button background */
    color: #f0f2f6;
    border: 1px solid #30363d;
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
    font-family: 'Open Sans', sans-serif; /* Consistent font */
}
.stButton > button:hover {
    background-color: #30363d; /* Slightly lighter on hover */
    border-color: #58a6ff;
    color: #58a6ff;
}
.stButton > button.primary {
    background-color: #238636; /* Primary button color */
    border-color: #238636;
    color: white;
}
.stButton > button.primary:hover {
    background-color: #2ea043;
    border-color: #2ea043;
}

/* Slot Grid Display */
.slot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); /* Responsive grid */
    gap: 12px; /* Slightly increased gap */
    max-width: 900px;
    margin-top: 20px;
    margin-bottom: 40px;
}
.slot {
    padding: 18px 0; /* More padding */
    text-align: center;
    border-radius: 6px;
    font-weight: 700;
    color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2); /* Subtle shadow for depth */
    font-family: 'Open Sans', sans-serif; /* Consistent font */
}
.free { background-color: #28a745; } /* Green */
.busy { background-color: #dc3545; } /* Red */
.mine { background-color: #007bff; } /* Blue */
small {
    font-weight: 400;
    opacity: 0.8;
    font-size: 0.8em; /* Slightly smaller text */
}

/* Messages */
.stAlert {
    border-radius: 5px;
    font-family: 'Open Sans', sans-serif; /* Consistent font */
}

/* Divider */
.st-emotion-cache-nahz7x { /* Streamlit divider element */
    background-color: #30363d;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* Import Google Fonts for 'Playfair Display' and 'Montserrat' */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Open+Sans:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');

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
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
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

# ---------- AUTH ----------
if st.session_state.user_id is None:
    # Using st.title for the main heading on the login/register screen
    st.title("🅿️ Parking Slot Booking")

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
col1, col2, col3 = st.columns([6, 3, 1])
with col1:
    # Using st.title for the main heading in the header
    st.title("🅿️ Parking Slot Booking")
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

# ---------- SLOTS ----------
slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# Using st.header for the dashboard section heading
st.header("🅿️ Parking Dashboard")

st.divider() # Added a divider for clear section separation

# ---------- ACTIVE BOOKING STATUS ----------
now_dt = datetime.now()

cur.execute("""
SELECT slot_number, start_datetime, end_datetime
FROM bookings
WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime
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
    else:
        st.info("🟢 No active parking session")

with col2:
    cur.execute("SELECT COUNT(*) FROM bookings")
    total = cur.fetchone()[0]

    st.metric("Total Bookings", total)
    
# ---------- LIVE AVAILABILITY ----------
st.subheader("📊 Live Slot Availability (Now)") # Using st.subheader

now = datetime.now().strftime("%Y-%m-%d %H:%M")

cur.execute("""
SELECT slot_number FROM bookings
WHERE? BETWEEN start_datetime AND end_datetime
""", (now,))
occupied = {r[0] for r in cur.fetchall()}

cur.execute("""
SELECT slot_number FROM bookings
WHERE user_id=? AND? BETWEEN start_datetime AND end_datetime
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
st.subheader("📅 Book Parking Slot") # Using st.subheader

booking_date = st.date_input("Date", min_value=date.today())

entry_time = st.time_input(
    "Entry Time",
    value=datetime.now().replace(second=0, microsecond=0).time()
)

exit_time = st.time_input("Exit Time")

start_dt = datetime.combine(booking_date, entry_time)
end_dt = datetime.combine(booking_date, exit_time)

next_day = False
if exit_time <= entry_time:
    next_day = True
    st.warning("Exit time is earlier than entry time. Booking will extend to next day.")

if next_day:
    end_dt += timedelta(days=1)

# Check blocked slots dynamically
cur.execute("""
SELECT slot_number FROM bookings
WHERE NOT (end_datetime <=? OR start_datetime >=?)
""", (
    start_dt.strftime("%Y-%m-%d %H:%M"),
    end_dt.strftime("%Y-%m-%d %H:%M")
))

blocked = {r[0] for r in cur.fetchall()}
available = [s for s in slots if s not in blocked]

if available:
    slot = st.selectbox("Available Slots", available)
else:
    st.error("No slots available for selected time")
    slot = None

if st.button("Confirm Booking"):

    if slot is None:
        st.error("No slot selected")
        st.stop()

    # Check overlapping booking for user
    cur.execute("""
    SELECT id FROM bookings
    WHERE user_id=?
    AND NOT (end_datetime <=? OR start_datetime >=?)
    """, (
        st.session_state.user_id,
        start_dt.strftime("%Y-%m-%d %H:%M"),
        end_dt.strftime("%Y-%m-%d %H:%M")
    ))

    existing = cur.fetchone()

    if existing:
        st.error("You already have a booking during this time. Only one car allowed.")
    else:
        cur.execute("""
        INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime)
        VALUES (?,?,?,?)
        """, (
            st.session_state.user_id,
            slot,
            start_dt.strftime("%Y-%m-%d %H:%M"),
            end_dt.strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        st.success(f"Slot {slot} booked successfully")
        st.rerun()
