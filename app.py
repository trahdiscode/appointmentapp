import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ParkOS", layout="wide", page_icon="🅿️")

# ---------- AUTO REFRESH (1 SECOND) ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- STYLESHEET ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg: #0D0E11;
    --surface: #13151A;
    --surface-2: #1A1D25;
    --border: rgba(255,255,255,0.07);
    --border-hover: rgba(255,255,255,0.14);
    --text-1: #F0F1F3;
    --text-2: #8B8FA8;
    --text-3: #52566A;
    --accent: #4F78FF;
    --accent-soft: rgba(79,120,255,0.12);
    --green: #22C55E;
    --green-soft: rgba(34,197,94,0.10);
    --red: #F25C5C;
    --red-soft: rgba(242,92,92,0.10);
    --amber: #F59E0B;
    --amber-soft: rgba(245,158,11,0.10);
    --radius: 10px;
    --radius-sm: 6px;
    --font: 'DM Sans', sans-serif;
    --font-mono: 'DM Mono', monospace;
}

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body,.stApp { background: var(--bg)!important; font-family: var(--font); color: var(--text-1); }
.main.block-container { padding: 2rem 2.5rem!important; max-width: 1200px!important; }
p, li, span { color: var(--text-1); font-size: 0.9rem; line-height: 1.6; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hover); border-radius: 9999px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stDecoration"] { display: none; }

/* ── Typography ── */
h1, h2, h3, h4 { font-family: var(--font); letter-spacing: -0.03em; }
h1 { font-size: 1.6rem; font-weight: 600; color: var(--text-1); }
h2 { font-size: 1.15rem; font-weight: 600; color: var(--text-1); margin: 2rem 0 1rem; }
h3 { font-size: 0.95rem; font-weight: 500; color: var(--text-2); margin: 1.25rem 0 0.5rem; }

/* ── Section label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 0.75rem;
    display: block;
}

/* ── Header ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.app-brand {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}
.app-brand-name {
    font-size: 2.2rem; /* INCREASED FONT SIZE FOR PARKOS */
    font-weight: 600;
    color: var(--text-1);
    letter-spacing: -0.04em;
}
.app-brand-badge {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--accent);
    background: var(--accent-soft);
    border: 1px solid rgba(79,120,255,0.2);
    padding: 2px 7px;
    border-radius: 4px;
    letter-spacing: 0.05em;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: var(--border-hover); }
.card-active {
    border-color: rgba(34,197,94,0.25);
    background: linear-gradient(135deg, rgba(34,197,94,0.05) 0%, var(--surface) 60%);
}

/* ── Stat blocks ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.stat-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
}
.stat-label { font-size: 0.72rem; font-weight: 500; color: var(--text-3); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.35rem; }
.stat-value { font-family: var(--font-mono); font-size: 2rem; font-weight: 400; color: var(--text-1); line-height: 1; }
.stat-value.green { color: var(--green); }
.stat-value.accent { color: var(--accent); }

/* ── Active parking card ── */
.active-card {
    background: var(--surface);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.active-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--green), transparent);
}
.active-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 0.75rem;
}
.active-dot {
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.active-slot { font-family: var(--font-mono); font-size: 2.5rem; font-weight: 400; color: var(--text-1); line-height: 1; margin-bottom: 0.5rem; }
.active-meta { font-size: 0.82rem; color: var(--text-2); margin-bottom: 0.25rem; }
.active-remaining { font-family: var(--font-mono); font-size: 1.2rem; color: var(--green); margin-top: 0.75rem; }

/* ── Booking list items ── */
.booking-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.booking-item:hover { border-color: var(--border-hover); }
.booking-slot {
    font-family: var(--font-mono);
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--text-1);
    min-width: 44px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 4px 10px;
    text-align: center;
}
.booking-details { flex: 1; }
.booking-status-badge {
    display: inline-block;
    font-size: 0.67rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 4px;
}
.badge-active { background: var(--green-soft); color: var(--green); border: 1px solid rgba(34,197,94,0.2); }
.badge-upcoming { background: var(--accent-soft); color: var(--accent); border: 1px solid rgba(79,120,255,0.2); }
.badge-completed { background: var(--surface-2); color: var(--text-3); border: 1px solid var(--border); }
.booking-time { font-size: 0.8rem; color: var(--text-2); font-family: var(--font-mono); }

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* ── Step header ── */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}
.step-num {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: var(--accent-soft);
    border: 1px solid rgba(79,120,255,0.25);
    color: var(--accent);
    font-size: 0.7rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.step-title { font-size: 0.85rem; font-weight: 500; color: var(--text-2); }

/* ── Slot grid ── */
.slot-legend {
    display: flex;
    gap: 1.25rem;
    margin-bottom: 1rem;
    align-items: center;
}
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: var(--text-2); }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.legend-free { background: var(--green); }
.legend-busy { background: var(--red); }
.legend-selected { background: var(--accent); }

/* ── Streamlit overrides ── */

/* Inputs */
.stTextInput > label,.stDateInput > label,.stTimeInput > label,.stSelectbox > label {
    font-size: 0.75rem!important;
    font-weight: 500!important;
    letter-spacing: 0.04em!important;
    text-transform: uppercase!important;
    color: var(--text-3)!important;
    margin-bottom: 4px!important;
}
.stTextInput input,.stDateInput input,.stTimeInput input {
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius-sm)!important;
    color: var(--text-1)!important;
    font-family: var(--font-mono)!important;
    font-size: 0.88rem!important;
    padding: 0.6rem 0.9rem!important;
    transition: border-color 0.2s, box-shadow 0.2s!important;
}
.stTextInput input:focus,.stDateInput input:focus,.stTimeInput input:focus {
    border-color: var(--accent)!important;
    box-shadow: 0 0 0 3px rgba(79,120,255,0.12)!important;
    outline: none!important;
}

/* Buttons */
.stButton > button {
    font-family: var(--font)!important;
    font-size: 0.85rem!important;
    font-weight: 500!important;
    border-radius: var(--radius-sm)!important;
    transition: all 0.18s ease!important;
    min-height: 40px!important;
}
.stButton > button[kind="primary"],.stButton > button[data-testid*="primary"] {
    background: var(--accent)!important;
    border: 1px solid var(--accent)!important;
    color: #fff!important;
}
.stButton > button[kind="primary"]:hover {
    background: #6088FF!important;
    box-shadow: 0 4px 16px rgba(79,120,255,0.3)!important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    color: var(--text-2)!important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--border-hover)!important;
    color: var(--text-1)!important;
    background: var(--surface-2)!important;
}

/* Slot buttons */
div[data-testid="stHorizontalBlock"].stButton > button {
    height: 52px!important;
    font-family: var(--font-mono)!important;
    font-size: 0.85rem!important;
    font-weight: 500!important;
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    color: var(--text-2)!important;
}
div[data-testid="stHorizontalBlock"].stButton > button:disabled {
    opacity: 0.35!important;
    cursor: not-allowed!important;
}

/* Alerts */
div[data-testid="stAlert"] {
    background: var(--surface)!important;
    border-radius: var(--radius)!important;
    border: 1px solid var(--border)!important;
    border-left: 3px solid!important;
    font-size: 0.85rem!important;
}
div[data-testid="stAlert"] p { font-size: 0.85rem!important; }

/* Metrics */
div[data-testid="stMetric"] {
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius)!important;
    padding: 1.25rem 1.5rem!important;
}
div[data-testid="stMetric"] label {
    font-size: 0.72rem!important;
    text-transform: uppercase!important;
    letter-spacing: 0.06em!important;
    color: var(--text-3)!important;
    white-space: normal!important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: var(--font-mono)!important;
    font-size: 2rem!important;
    font-weight: 400!important;
    color: var(--text-1)!important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent!important;
    border-bottom: 1px solid var(--border)!important;
    gap: 0!important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent!important;
    border: none!important;
    color: var(--text-2)!important;
    font-size: 0.85rem!important;
    font-weight: 500!important;
    padding: 0.6rem 1.25rem!important;
    border-radius: 0!important;
    border-bottom: 2px solid transparent!important;
    transition: all 0.2s!important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-1)!important; }
.stTabs [aria-selected="true"] {
    color: var(--text-1)!important;
    border-bottom-color: var(--accent)!important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem!important; }

/* Columns gap */
div[data-testid="stHorizontalBlock"] { gap: 0.5rem!important; }

/* Info block */
.info-empty {
    background: var(--surface);
    border: 1px dashed var(--border-hover);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
    color: var(--text-3);
    font-size: 0.85rem;
}

/* Confirm slot banner */
.confirm-banner {
    background: var(--surface);
    border: 1px solid rgba(79,120,255,0.25);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1rem 0;
    gap: 1rem;
}
.confirm-banner-text { font-size: 0.88rem; color: var(--text-2); }
.confirm-banner-slot { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 500; color: var(--text-1); }

/* Login page */
.login-container {
    max-width: 420px;
    margin: 4rem auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: calc(var(--radius) * 1.5);
    padding: 2.5rem;
}
.login-logo {
    font-size: 2.2rem; /* INCREASED FONT SIZE FOR PARKOS LOGIN */
    font-weight: 700;
    letter-spacing: -0.06em;
    color: var(--text-1);
    margin-bottom: 0.25rem;
}
.login-tagline {
    font-size: 0.8rem;
    color: var(--text-3);
    margin-bottom: 2rem;
}

/* Warning inline */
.warn-note {
    font-size: 0.78rem;
    color: var(--amber);
    background: var(--amber-soft);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: var(--radius-sm);
    padding: 0.5rem 0.9rem;
    margin-top: 0.5rem;
}

@media (max-width: 768px) {
   .main.block-container { padding: 1rem 1.25rem!important; }
   .stat-grid { grid-template-columns: 1fr 1fr; }
   .app-header { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
   .booking-item { flex-wrap: wrap; }
}
@media (max-width: 480px) {
   .stat-grid { grid-template-columns: 1fr; }
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
        conn.commit(); return True
    except sqlite3.IntegrityError: return False

# ---------- SESSION STATE ----------
if 'selected_slot' not in st.session_state:
    st.session_state.selected_slot = None

# ---------- AUTH PAGE ----------
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.markdown("""
    <div style="max-width:420px;margin:3rem auto;">
        <div style="margin-bottom:2rem;">
            <div class="login-logo">ParkOS</div>
            <div style="font-size:0.8rem;color:var(--text-3);margin-top:2px;">Intelligent Parking Management</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_center, = [st.columns([1])[0]]
    with col_center:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            if st.button("Sign In", type="primary", use_container_width=True):
                user = get_user(u, p)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.vehicle_number = user[1]
                    st.rerun()
                else: st.error("Invalid username or password.")
        with tab2:
            u = st.text_input("Choose a Username", key="reg_user")
            p = st.text_input("Choose a Password", type="password", key="reg_pass")
            if st.button("Create Account", type="primary", use_container_width=True):
                if create_user(u, p): st.success("Account created — sign in to continue.")
                else: st.error("That username is already taken.")
    st.stop()

# ---------- MAIN APP ----------

# Header
st.markdown(f"""
<div class="app-header">
    <div class="app-brand">
        <span class="app-brand-name">ParkOS</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Sign Out", type="secondary"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# Vehicle number gate
if 'vehicle_number' not in st.session_state or st.session_state.vehicle_number is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Register Your Vehicle")
    st.markdown("<p style='color:var(--text-2);'>This is a one-time setup. Your vehicle number will be associated with all future bookings.</p>", unsafe_allow_html=True)
    v = st.text_input("Vehicle Number", placeholder="e.g., TN01 AB1234")
    if st.button("Save & Continue", type="primary", use_container_width=True):
        if v.strip():
            cur.execute("UPDATE users SET vehicle_number=? WHERE id=?", (v.upper(), st.session_state.user_id))
            conn.commit(); st.session_state.vehicle_number = v.upper(); st.rerun()
        else: st.error("Please enter a valid vehicle number.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Data ──
now_dt = datetime.now()
user_current_future = cur.execute(
    "SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? AND end_datetime >? ORDER BY start_datetime",
    (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))
).fetchall()

total_bookings = cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id=?", (st.session_state.user_id,)).fetchone()[0]
active_booking = next(
    (b for b in user_current_future
     if datetime.strptime(b[2], "%Y-%m-%d %H:%M") <= now_dt <= datetime.strptime(b[3], "%Y-%m-%d %H:%M")), None
)
user_has_active_or_future = bool(user_current_future)

# ── Dashboard ──
st.markdown('<span class="section-label">Overview</span>', unsafe_allow_html=True)

dash_col1, dash_col2 = st.columns([1.6, 1])

with dash_col1:
    if active_booking:
        _, slot_num, start_str, end_str = active_booking
        end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
        remaining = end_dt - now_dt
        remaining_str = str(remaining).split('.')[0]
        st.markdown(f"""
        <div class="active-card">
            <div class="active-label"><span class="active-dot"></span> Active Session</div>
            <div class="active-slot">{slot_num}</div>
            <div class="active-meta">Vehicle: <strong style="color:var(--text-1);">{st.session_state.vehicle_number}</strong></div>
            <div class="active-meta">Until <strong style="color:var(--text-1);">{end_dt.strftime('%I:%M %p')}</strong>
              &nbsp;·&nbsp; {end_dt.strftime('%b %d')}</div>
            <div class="active-remaining">⏱ {remaining_str} remaining</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-empty">
            <div style="font-size:1.4rem;margin-bottom:0.4rem;">🅿️</div>
            No active parking session
        </div>
        """, unsafe_allow_html=True)

with dash_col2:
    st.markdown(f"""
    <div class="stat-block">
        <div class="stat-label">Total Bookings</div>
        <div class="stat-value accent">{total_bookings}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Manage Bookings ──
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<span class="section-label">Your Bookings</span>', unsafe_allow_html=True)

if user_current_future:
    for booking_id, slot_number, start_dt_str, end_dt_str in user_current_future:
        start_dt_obj = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
        end_dt_obj = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M")
        is_active = (start_dt_obj <= now_dt <= end_dt_obj)
        is_future = (start_dt_obj > now_dt)

        badge_class = "badge-active" if is_active else "badge-upcoming"
        badge_text = "Active" if is_active else "Upcoming"
        btn_label = "End Early" if is_active else "Cancel"
        btn_key = f"{'end' if is_active else 'cancel'}_booking_{booking_id}"

        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"""
            <div class="booking-item">
                <div class="booking-slot">{slot_number}</div>
                <div class="booking-details">
                    <span class="booking-status-badge {badge_class}">{badge_text}</span><br>
                    <span class="booking-time">{start_dt_obj.strftime('%b %d · %I:%M %p')} → {end_dt_obj.strftime('%I:%M %p')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True) # Spacer for alignment
            if st.button(btn_label, key=btn_key, type="secondary", use_container_width=True):
                if st.session_state.get(f"confirm_{btn_key}", False):
                    cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                    conn.commit()
                    del st.session_state[f"confirm_{btn_key}"]
                    st.session_state.selected_slot = None
                    st.rerun()
                else:
                    st.session_state[f"confirm_{btn_key}"] = True
                    st.warning("Click again to confirm.")
else:
    st.markdown('<div class="info-empty">No current booking.</div>', unsafe_allow_html=True)

# Past bookings
past_bookings = cur.execute(
    "SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? AND end_datetime <=? ORDER BY start_datetime DESC",
    (st.session_state.user_id, now_dt.strftime("%Y-%m-%d %H:%M"))
).fetchall()

if past_bookings:
    with st.expander(f"Booking History ({len(past_bookings)})"):
        for _, slot_number, start_dt_str, end_dt_str in past_bookings:
            s = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
            e = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M")
            st.markdown(f"""
            <div class="booking-item" style="opacity:0.6;">
                <div class="booking-slot" style="color:var(--text-3);">{slot_number}</div>
                <div class="booking-details">
                    <span class="booking-status-badge badge-completed">Completed</span><br>
                    <span class="booking-time">{s.strftime('%b %d · %I:%M %p')} → {e.strftime('%I:%M %p')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Book New Slot ──
st.markdown('<hr class="divider">', unsafe_allow_html=True)

if not user_has_active_or_future:
    st.markdown('<span class="section-label">New Booking</span>', unsafe_allow_html=True)

    # Step 1
    st.markdown("""
    <div class="step-header">
        <span class="step-num">1</span>
        <span class="step-title">Select your parking window</span>
    </div>
    """, unsafe_allow_html=True)

    col_d, col_en, col_ex = st.columns(3)
    with col_d:
        booking_date = st.date_input("Date", min_value=date.today(), key="booking_date_input")
    with col_en:
        entry_time = st.time_input("Entry Time", value=datetime.now().replace(second=0, microsecond=0).time(), key="entry_time_input")
    with col_ex:
        exit_time = st.time_input("Exit Time", key="exit_time_input")

    start_dt = datetime.combine(booking_date, entry_time)
    end_dt = datetime.combine(booking_date, exit_time)
    next_day_note = False
    if exit_time <= entry_time:
        end_dt += timedelta(days=1)
        next_day_note = True

    if next_day_note:
        st.markdown('<div class="warn-note">⚠️ Exit time is before entry — booking extends to the next day.</div>', unsafe_allow_html=True)

    # Step 2
    st.markdown("""
    <div class="step-header" style="margin-top:1.5rem;">
        <span class="step-num">2</span>
        <span class="step-title">Choose an available slot</span>
    </div>
    """, unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div class="slot-legend">
        <div class="legend-item"><div class="legend-dot legend-free"></div> Available</div>
        <div class="legend-item"><div class="legend-dot legend-busy"></div> Occupied</div>
        <div class="legend-item"><div class="legend-dot legend-selected"></div> Selected</div>
    </div>
    """, unsafe_allow_html=True)

    blocked = {r[0] for r in cur.execute(
        "SELECT slot_number FROM bookings WHERE NOT (end_datetime <=? OR start_datetime >=?)",
        (start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))
    ).fetchall()}

    def handle_slot_click(slot_name):
        if st.session_state.selected_slot == slot_name: st.session_state.selected_slot = None
        else: st.session_state.selected_slot = slot_name

    slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

    # Dynamic slot button styles
    slot_css = ""
    for s in slots:
        is_blocked = s in blocked
        is_selected = s == st.session_state.selected_slot
        sel = f'button[data-testid*="slot_{s}"]'
        if is_selected:
            slot_css += f"""{sel} {{
                background: var(--accent-soft)!important;
                border: 1.5px solid var(--accent)!important;
                color: var(--accent)!important;
            }}\n"""
        elif is_blocked:
            slot_css += f"""{sel} {{
                background: var(--red-soft)!important;
                border: 1px solid rgba(242,92,92,0.2)!important;
                color: var(--red)!important;
                cursor: not-allowed!important;
            }}\n"""
        else:
            slot_css += f"""{sel} {{
                border-left: 2px solid var(--green)!important;
                color: var(--text-1)!important;
            }}\n"""
            slot_css += f"""{sel}:hover {{
                background: var(--green-soft)!important;
                border-color: var(--green)!important;
                color: var(--green)!important;
            }}\n"""

    st.markdown(f"<style>{slot_css}</style>", unsafe_allow_html=True)

    # Row labels
    for row_prefix in ['A', 'B']:
        row_slots = [f"{row_prefix}{i}" for i in range(1, 11)]
        st.markdown(f'<span style="font-size:0.7rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--text-3);font-weight:600;">Row {row_prefix}</span>', unsafe_allow_html=True)
        cols = st.columns(10)
        for j, s in enumerate(row_slots):
            with cols[j]:
                is_blocked = s in blocked
                is_disabled = is_blocked or (st.session_state.selected_slot is not None and st.session_state.selected_slot!= s)
                st.button(s, key=f"slot_{s}", on_click=handle_slot_click, args=(s,), disabled=is_disabled, use_container_width=True)

    # Confirmation
    if st.session_state.selected_slot:
        if st.session_state.selected_slot in blocked:
            st.error(f"Slot {st.session_state.selected_slot} is no longer available.")
            st.session_state.selected_slot = None
            st.rerun()
        else:
            st.markdown(f"""
            <div class="confirm-banner">
                <div>
                    <div style="font-size:0.72rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;">Selected Slot</div>
                    <div class="confirm-banner-slot">{st.session_state.selected_slot}</div>
                    <div style="font-size:0.78rem;color:var(--text-2);margin-top:3px;">{start_dt.strftime('%b %d, %I:%M %p')} → {end_dt.strftime('%I:%M %p')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Confirm Booking →", type="primary", use_container_width=True):
                cur.execute(
                    "INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)",
                    (st.session_state.user_id, st.session_state.selected_slot,
                     start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))
                )
                conn.commit()
                st.success(f"Slot {st.session_state.selected_slot} booked successfully.")
                st.session_state.selected_slot = None
                st.rerun()
    else:
        st.markdown('<div class="info-empty" style="margin-top:0.75rem;">Select an available slot above to continue.</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-empty">
        <div style="font-size:1.2rem;margin-bottom:0.4rem;">🔒</div>
        You have an active booking.<br>
        <span style="font-size:0.78rem;">Manage your existing sessions above to make a new booking.</span>
    </div>
    """, unsafe_allow_html=True)
