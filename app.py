import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh
import pytz

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ParkOS", layout="wide", page_icon="🅿️", initial_sidebar_state="collapsed")

# ---------- AUTO REFRESH ----------
st_autorefresh(interval=1000, key="refresh")

# ---------- STYLESHEET ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #080A0F;
    --bg-grad: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(99,102,241,0.15) 0%, transparent 70%);
    --surface: #0F1117;
    --surface-2: #161923;
    --surface-3: #1E2230;
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --border-active: rgba(99,102,241,0.4);
    --text-1: #F1F2F6;
    --text-2: #9397B0;
    --text-3: #4B5068;
    --accent: #6366F1;
    --accent-2: #818CF8;
    --accent-soft: rgba(99,102,241,0.1);
    --green: #10B981;
    --green-soft: rgba(16,185,129,0.08);
    --green-border: rgba(16,185,129,0.2);
    --red: #EF4444;
    --red-soft: rgba(239,68,68,0.08);
    --amber: #F59E0B;
    --amber-soft: rgba(245,158,11,0.1);
    --radius: 14px;
    --radius-sm: 8px;
    --radius-xs: 5px;
    --font: 'Outfit', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
    --shadow-accent: 0 4px 20px rgba(99,102,241,0.25);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
    background: var(--bg)!important;
    font-family: var(--font);
    color: var(--text-1);
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: var(--bg-grad);
    pointer-events: none;
    z-index: 0;
}
.main.block-container {
    padding: 1.5rem 1.25rem 4rem!important;
    max-width: 480px!important;
    margin: 0 auto!important;
    position: relative;
    z-index: 1;
}

/* Desktop layout */
@media (min-width: 769px) {
    .main.block-container {
        padding: 2rem 2rem 4rem!important;
        max-width: 900px!important;
    }
}

p, li { color: var(--text-1); font-size: 0.9rem; line-height: 1.6; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hover); border-radius: 9999px; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, div[data-testid="stDecoration"] { display: none; }

h1, h2, h3, h4 { font-family: var(--font); letter-spacing: -0.02em; }

/* ── Section label ── */
.section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── App Header ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.25rem;
    margin-bottom: 1.5rem;
}
.app-brand {
    display: flex;
    align-items: center;
    gap: 0.625rem;
}
.app-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--accent) 0%, #818CF8 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: var(--shadow-accent);
}
.app-brand-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-1);
    letter-spacing: -0.04em;
}
.app-brand-sub {
    font-size: 0.6rem;
    font-weight: 600;
    color: var(--text-3);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    line-height: 1;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.user-pill {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 4px 10px 4px 6px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: var(--text-2);
}
.user-avatar {
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, var(--accent) 0%, #818CF8 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-weight: 700;
    color: white;
}

/* ── Active session card ── */
.active-card {
    background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, var(--surface) 60%);
    border: 1px solid var(--green-border);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.active-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--green), transparent 60%);
}
.active-card-glow {
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.active-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--green);
    background: var(--green-soft);
    border: 1px solid var(--green-border);
    padding: 3px 8px;
    border-radius: 99px;
    margin-bottom: 0.75rem;
}
.active-dot {
    width: 5px; height: 5px;
    background: var(--green);
    border-radius: 50%;
    animation: pulse-dot 2s ease infinite;
    display: inline-block;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.75); }
}
.active-slot-display {
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
    margin: 0.5rem 0 0.75rem;
}
.active-slot-label {
    font-size: 0.65rem;
    color: var(--text-3);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.active-slot-num {
    font-family: var(--font-mono);
    font-size: 3rem;
    font-weight: 600;
    color: var(--text-1);
    line-height: 1;
}
.active-time-block {
    flex: 1;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.5rem 0.75rem;
}
.active-time-label { font-size: 0.6rem; color: var(--text-3); font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
.active-time-val { font-family: var(--font-mono); font-size: 0.95rem; color: var(--text-1); font-weight: 500; }
.active-remaining-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 0.875rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin-top: 0.25rem;
}
.remaining-label { font-size: 0.7rem; color: var(--text-3); font-weight: 500; flex: 1; }
.remaining-val { font-family: var(--font-mono); font-size: 0.9rem; color: var(--green); font-weight: 600; }
.vehicle-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 8px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-2);
    margin-bottom: 0.75rem;
}

/* ── Stats row ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.625rem;
    margin-bottom: 1.25rem;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.125rem;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 40px; height: 40px;
    border-radius: 50%;
    background: var(--accent-soft);
    transform: translate(10px, 10px);
}
.stat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 0.35rem;
}
.stat-value {
    font-family: var(--font-mono);
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--text-1);
    line-height: 1;
}
.stat-value.accent { color: var(--accent-2); }
.stat-value.green { color: var(--green); }

/* ── Empty state ── */
.empty-card {
    background: var(--surface);
    border: 1px dashed var(--border-hover);
    border-radius: var(--radius);
    padding: 2rem 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.empty-title { font-size: 0.9rem; font-weight: 600; color: var(--text-2); margin-bottom: 0.25rem; }
.empty-sub { font-size: 0.78rem; color: var(--text-3); }

/* ── Booking items ── */
.booking-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 0.625rem;
    transition: border-color 0.2s;
}
.booking-card:hover { border-color: var(--border-hover); }
.booking-card-inner {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 0.875rem;
    padding: 0.875rem 1rem;
}
.slot-badge {
    width: 48px;
    height: 48px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-1);
    flex-shrink: 0;
}
.slot-badge.active { background: var(--green-soft); border-color: var(--green-border); color: var(--green); }
.booking-info { min-width: 0; }
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 99px;
    margin-bottom: 4px;
}
.pill-active { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }
.pill-upcoming { background: var(--accent-soft); color: var(--accent-2); border: 1px solid rgba(99,102,241,0.2); }
.pill-completed { background: var(--surface-2); color: var(--text-3); border: 1px solid var(--border); }
.booking-time-text {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--text-2);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.booking-date-text {
    font-size: 0.7rem;
    color: var(--text-3);
    margin-top: 1px;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Step header ── */
.step-wrap {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    margin-bottom: 1rem;
}
.step-num {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: var(--accent-soft);
    border: 1px solid rgba(99,102,241,0.25);
    color: var(--accent-2);
    font-size: 0.7rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.step-title { font-size: 0.875rem; font-weight: 600; color: var(--text-2); }

/* ── Time pickers ── */
.time-form {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* ── Slot legend ── */
.slot-legend {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.875rem;
    flex-wrap: wrap;
}
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: var(--text-2); }
.legend-dot { width: 8px; height: 8px; border-radius: 3px; flex-shrink: 0; }
.legend-free { background: var(--green); }
.legend-busy { background: var(--red); }
.legend-selected { background: var(--accent); }

/* ── Row label ── */
.row-label {
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    font-weight: 700;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.row-label::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 10px;
    background: var(--accent);
    border-radius: 99px;
}

/* ── Confirm banner ── */
.confirm-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, var(--surface) 60%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}
.confirm-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent 60%);
}
.confirm-slot-big {
    font-family: var(--font-mono);
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-1);
    line-height: 1;
    margin: 0.25rem 0;
}
.confirm-time {
    font-size: 0.78rem;
    color: var(--text-2);
    font-family: var(--font-mono);
}

/* ── Warning / note ── */
.warn-note {
    font-size: 0.78rem;
    color: var(--amber);
    background: var(--amber-soft);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: var(--radius-sm);
    padding: 0.625rem 1rem;
    margin-top: 0.625rem;
}
.lock-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 1.25rem;
    text-align: center;
}
.lock-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
.lock-title { font-size: 0.95rem; font-weight: 600; color: var(--text-2); margin-bottom: 0.375rem; }
.lock-sub { font-size: 0.78rem; color: var(--text-3); line-height: 1.5; }

/* ── Login page ── */
.login-wrap {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
}
.login-card {
    width: 100%;
    max-width: 380px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: calc(var(--radius) * 1.5);
    padding: 2rem;
    box-shadow: var(--shadow-lg);
}
.login-logo {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    margin-bottom: 0.25rem;
}
.login-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent) 0%, #818CF8 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    box-shadow: var(--shadow-accent);
}
.login-logo-text {
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    color: var(--text-1);
}
.login-tagline { font-size: 0.78rem; color: var(--text-3); margin-bottom: 1.75rem; }

/* ── Streamlit overrides ── */
.stTextInput > label, .stDateInput > label, .stTimeInput > label, .stSelectbox > label {
    font-family: var(--font)!important;
    font-size: 0.7rem!important;
    font-weight: 700!important;
    letter-spacing: 0.08em!important;
    text-transform: uppercase!important;
    color: var(--text-3)!important;
    margin-bottom: 4px!important;
}
.stTextInput input, .stDateInput input, .stTimeInput input {
    background: var(--surface-2)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius-sm)!important;
    color: var(--text-1)!important;
    font-family: var(--font-mono)!important;
    font-size: 0.9rem!important;
    padding: 0.625rem 0.875rem!important;
    transition: border-color 0.2s, box-shadow 0.2s!important;
    min-height: 44px!important;
}
.stTextInput input:focus, .stDateInput input:focus {
    border-color: var(--accent)!important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12)!important;
    outline: none!important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: var(--surface-2)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius-sm)!important;
    color: var(--text-1)!important;
    min-height: 44px!important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent)!important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12)!important;
}
div[data-baseweb="popover"] { background: var(--surface-2)!important; border: 1px solid var(--border)!important; border-radius: var(--radius)!important; }
[data-baseweb="menu"] { background: var(--surface-2)!important; }
[data-baseweb="option"] { background: var(--surface-2)!important; color: var(--text-1)!important; font-size: 0.88rem!important; }
[data-baseweb="option"]:hover, [aria-selected="true"] { background: var(--surface-3)!important; }

/* Buttons */
.stButton > button {
    font-family: var(--font)!important;
    font-size: 0.88rem!important;
    font-weight: 600!important;
    border-radius: var(--radius-sm)!important;
    transition: all 0.18s ease!important;
    min-height: 44px!important;
    letter-spacing: 0.01em!important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent) 0%, #818CF8 100%)!important;
    border: none!important;
    color: #fff!important;
    box-shadow: var(--shadow-accent)!important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 24px rgba(99,102,241,0.4)!important;
    transform: translateY(-1px)!important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2)!important;
    border: 1px solid var(--border)!important;
    color: var(--text-2)!important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--border-hover)!important;
    color: var(--text-1)!important;
}

/* Slot buttons */
.stButton > button[key*="slot_"] {
    height: 48px!important;
    font-family: var(--font-mono)!important;
    font-size: 0.8rem!important;
    font-weight: 600!important;
    padding: 0!important;
}

/* Alerts */
div[data-testid="stAlert"] {
    background: var(--surface)!important;
    border-radius: var(--radius)!important;
    border: 1px solid var(--border)!important;
    font-size: 0.85rem!important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius)!important;
    padding: 1rem 1.25rem!important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface)!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius-sm)!important;
    padding: 3px!important;
    gap: 2px!important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent!important;
    border: none!important;
    color: var(--text-2)!important;
    font-size: 0.85rem!important;
    font-weight: 600!important;
    padding: 0.5rem 1rem!important;
    border-radius: var(--radius-xs)!important;
    transition: all 0.2s!important;
    flex: 1!important;
    text-align: center!important;
    justify-content: center!important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-1)!important; }
.stTabs [aria-selected="true"] {
    background: var(--surface-3)!important;
    color: var(--text-1)!important;
    box-shadow: var(--shadow-sm)!important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem!important; }

div[data-testid="stHorizontalBlock"] { gap: 0.4rem!important; }

/* Expander */
details { border: 1px solid var(--border)!important; border-radius: var(--radius)!important; background: var(--surface)!important; }
summary { padding: 0.875rem 1rem!important; font-size: 0.85rem!important; color: var(--text-2)!important; font-weight: 600!important; }

/* Date input */
div[data-baseweb="calendar"] { background: var(--surface-2)!important; border: 1px solid var(--border)!important; border-radius: var(--radius)!important; }

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

ist_timezone = pytz.timezone('Asia/Kolkata')

def get_next_30min_slot_tz(dt_tz):
    minutes = dt_tz.minute
    if minutes == 0:
        return dt_tz.replace(second=0, microsecond=0)
    elif minutes <= 30:
        return dt_tz.replace(minute=30, second=0, microsecond=0)
    else:
        return (dt_tz + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

def build_time_options(for_date, min_dt=None):
    all_slots = [(datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").strftime("%I:%M %p"),
                  datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").time())
                 for h in range(24) for m in (0, 30)]
    if for_date == date.today() and min_dt is not None:
        cutoff = min_dt.time()
        all_slots = [(label, t) for label, t in all_slots if t >= cutoff]
    return all_slots

def parse_dt(s):
    dt_obj = datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")
    if dt_obj.tzinfo is None:
        return ist_timezone.localize(dt_obj)
    return dt_obj

# ---------- SESSION STATE ----------
if 'selected_slot' not in st.session_state:
    st.session_state.selected_slot = None

# ---------- AUTH PAGE ----------
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0 1.5rem;">
            <div style="display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;background:linear-gradient(135deg,#6366F1,#818CF8);border-radius:16px;margin-bottom:0.875rem;box-shadow:0 8px 24px rgba(99,102,241,0.3);">
                <span style="font-size:1.4rem;">🅿️</span>
            </div>
            <div style="font-size:2rem;font-weight:800;letter-spacing:-0.05em;color:#F1F2F6;line-height:1;">ParkOS</div>
            <div style="font-size:0.78rem;color:#4B5068;margin-top:0.25rem;letter-spacing:0.04em;">Smart Parking Management</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            u = st.text_input("Username", key="login_user", placeholder="Enter username")
            p = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            if st.button("Sign In →", type="primary", use_container_width=True):
                user = get_user(u, p)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.vehicle_number = user[1]
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with tab2:
            u = st.text_input("Choose a Username", key="reg_user", placeholder="Pick a username")
            p = st.text_input("Choose a Password", type="password", key="reg_pass", placeholder="Pick a password")
            if st.button("Create Account →", type="primary", use_container_width=True):
                if create_user(u, p):
                    st.success("Account created — sign in to continue.")
                else:
                    st.error("That username is already taken.")
    st.stop()

# ---------- MAIN APP ----------

# Fetch username if not set
if 'username' not in st.session_state:
    res = cur.execute("SELECT username FROM users WHERE id=?", (st.session_state.user_id,)).fetchone()
    st.session_state.username = res[0] if res else "User"

username = st.session_state.get('username', 'User')
avatar_letter = username[0].upper() if username else "U"

# Header
col_h1, col_h2 = st.columns([1, 'auto'])
with col_h1:
    st.markdown(f"""
    <div class="app-header">
        <div class="app-brand">
            <div class="app-icon">🅿️</div>
            <div>
                <div class="app-brand-name">ParkOS</div>
                <div class="app-brand-sub">Smart Parking</div>
            </div>
        </div>
        <div class="user-pill">
            <div class="user-avatar">{avatar_letter}</div>
            {username}
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.button("Sign Out", type="secondary"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# Vehicle number gate
if 'vehicle_number' not in st.session_state or st.session_state.vehicle_number is None:
    st.markdown("""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-top:1rem;">
        <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:0.5rem;">One-time Setup</div>
        <div style="font-size:1.05rem;font-weight:700;color:var(--text-1);margin-bottom:0.375rem;">Register Your Vehicle</div>
        <div style="font-size:0.82rem;color:var(--text-2);margin-bottom:1.25rem;">Your vehicle number will be linked to all future bookings.</div>
    </div>
    """, unsafe_allow_html=True)
    v = st.text_input("Vehicle Number", placeholder="e.g., TN01 AB1234")
    if st.button("Save & Continue →", type="primary", use_container_width=True):
        if v.strip():
            cur.execute("UPDATE users SET vehicle_number=? WHERE id=?", (v.upper(), st.session_state.user_id))
            conn.commit(); st.session_state.vehicle_number = v.upper(); st.rerun()
        else:
            st.error("Please enter a valid vehicle number.")
    st.stop()

# ── Current time ──
now_dt_fresh_ist = datetime.now(ist_timezone).replace(second=0, microsecond=0)
now_dt = now_dt_fresh_ist
earliest_allowed_dt_ist = get_next_30min_slot_tz(now_dt_fresh_ist)

# ── Fetch bookings ──
all_user_bookings = cur.execute(
    "SELECT id, slot_number, start_datetime, end_datetime FROM bookings WHERE user_id=? ORDER BY start_datetime",
    (st.session_state.user_id,)
).fetchall()

total_bookings = len(all_user_bookings)
user_current_future = [b for b in all_user_bookings if parse_dt(b[3]) > now_dt]
past_bookings_list = sorted(
    [b for b in all_user_bookings if parse_dt(b[3]) <= now_dt],
    key=lambda x: x[2], reverse=True
)
active_booking = next(
    (b for b in user_current_future if parse_dt(b[2]) <= now_dt <= parse_dt(b[3])), None
)
user_has_active_or_future = bool(user_current_future)
upcoming_count = len([b for b in user_current_future if parse_dt(b[2]) > now_dt])

# ── Overview ──
st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

# Stats row
st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">Total Bookings</div>
        <div class="stat-value accent">{total_bookings}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Upcoming</div>
        <div class="stat-value green">{upcoming_count}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Active session
if active_booking:
    _, slot_num, start_str, end_str = active_booking
    end_dt = parse_dt(end_str)
    start_dt_active = parse_dt(start_str)
    remaining = end_dt - now_dt
    remaining_str = str(remaining).split('.')[0]
    st.markdown(f"""
    <div class="active-card">
        <div class="active-card-glow"></div>
        <div class="active-badge"><span class="active-dot"></span> Active Session</div>
        <div class="vehicle-chip">🚗 {st.session_state.vehicle_number}</div>
        <div class="active-slot-display">
            <div>
                <div class="active-slot-label">Slot</div>
                <div class="active-slot-num">{slot_num}</div>
            </div>
            <div class="active-time-block">
                <div class="active-time-label">Parked until</div>
                <div class="active-time-val">{end_dt.strftime('%I:%M %p')}</div>
                <div style="font-size:0.65rem;color:var(--text-3);margin-top:2px;">{end_dt.strftime('%b %d')}</div>
            </div>
        </div>
        <div class="active-remaining-bar">
            <span class="remaining-label">⏱ Time remaining</span>
            <span class="remaining-val">{remaining_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-card">
        <div class="empty-icon">🅿️</div>
        <div class="empty-title">No Active Session</div>
        <div class="empty-sub">Park now using the booking section below</div>
    </div>
    """, unsafe_allow_html=True)

# ── Bookings ──
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Your Bookings</div>', unsafe_allow_html=True)

if user_current_future:
    for booking_id, slot_number, start_dt_str, end_dt_str in user_current_future:
        start_dt_obj = parse_dt(start_dt_str)
        end_dt_obj = parse_dt(end_dt_str)
        is_active_b = (start_dt_obj <= now_dt <= end_dt_obj)

        badge_class = "pill-active" if is_active_b else "pill-upcoming"
        badge_text = "Active" if is_active_b else "Upcoming"
        slot_class = "slot-badge active" if is_active_b else "slot-badge"
        btn_label = "End Early" if is_active_b else "Cancel"
        btn_key = f"{'end' if is_active_b else 'cancel'}_booking_{booking_id}"

        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"""
            <div class="booking-card">
                <div class="booking-card-inner">
                    <div class="{slot_class}">{slot_number}</div>
                    <div class="booking-info">
                        <span class="status-pill {badge_class}">{badge_text}</span>
                        <div class="booking-time-text">{start_dt_obj.strftime('%I:%M %p')} → {end_dt_obj.strftime('%I:%M %p')}</div>
                        <div class="booking-date-text">{start_dt_obj.strftime('%b %d, %Y')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            if st.button(btn_label, key=btn_key, type="secondary", use_container_width=True):
                if st.session_state.get(f"confirm_{btn_key}", False):
                    cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                    conn.commit()
                    del st.session_state[f"confirm_{btn_key}"]
                    st.session_state.selected_slot = None
                    st.rerun()
                else:
                    st.session_state[f"confirm_{btn_key}"] = True
                    st.warning("Tap again to confirm.")
else:
    st.markdown('<div class="empty-card" style="padding:1.25rem;"><div class="empty-sub">No current or upcoming bookings.</div></div>', unsafe_allow_html=True)

# Past bookings
if past_bookings_list:
    with st.expander(f"📋 Booking History ({len(past_bookings_list)})"):
        for _, slot_number, start_dt_str, end_dt_str in past_bookings_list:
            s = parse_dt(start_dt_str)
            e = parse_dt(end_dt_str)
            st.markdown(f"""
            <div class="booking-card" style="opacity:0.55;">
                <div class="booking-card-inner">
                    <div class="slot-badge" style="color:var(--text-3);">{slot_number}</div>
                    <div class="booking-info">
                        <span class="status-pill pill-completed">Completed</span>
                        <div class="booking-time-text">{s.strftime('%I:%M %p')} → {e.strftime('%I:%M %p')}</div>
                        <div class="booking-date-text">{s.strftime('%b %d, %Y')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Book New Slot ──
st.markdown('<hr class="divider">', unsafe_allow_html=True)

if not user_has_active_or_future:
    st.markdown('<div class="section-label">New Booking</div>', unsafe_allow_html=True)

    # Step 1
    st.markdown("""
    <div class="step-wrap">
        <span class="step-num">1</span>
        <span class="step-title">Select parking window</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="time-form">', unsafe_allow_html=True)
    booking_date = st.date_input("Date", min_value=date.today(), key="booking_date_input")

    entry_options = build_time_options(booking_date, min_dt=earliest_allowed_dt_ist)
    if not entry_options:
        st.warning("No available time slots for today. Please select a future date.")
        st.stop()

    entry_labels = [label for label, _ in entry_options]
    entry_times = [t for _, t in entry_options]

    col_en, col_ex = st.columns(2)
    with col_en:
        entry_label = st.selectbox("Entry Time", entry_labels, index=0, key="entry_select")
    selected_entry_time = entry_times[entry_labels.index(entry_label)]
    start_dt = ist_timezone.localize(datetime.combine(booking_date, selected_entry_time))

    exit_options_raw = [(datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").strftime("%I:%M %p"),
                         datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").time())
                        for h in range(24) for m in (0, 30)]
    exit_options = [(label, t) for label, t in exit_options_raw if t > selected_entry_time]
    if not exit_options:
        exit_options = exit_options_raw
    exit_labels = [label for label, _ in exit_options]
    exit_times = [t for _, t in exit_options]

    with col_ex:
        default_exit_idx = min(3, len(exit_labels) - 1)
        exit_label = st.selectbox("Exit Time", exit_labels, index=default_exit_idx, key="exit_select")
    st.markdown('</div>', unsafe_allow_html=True)

    selected_exit_time = exit_times[exit_labels.index(exit_label)]
    end_dt = ist_timezone.localize(datetime.combine(booking_date, selected_exit_time))

    next_day_note = False
    if selected_exit_time <= selected_entry_time:
        end_dt += timedelta(days=1)
        next_day_note = True

    if start_dt < now_dt_fresh_ist:
        st.markdown('<div class="warn-note">⚠️ Entry time is in the past. Please select a current or future time.</div>', unsafe_allow_html=True)
        st.stop()

    if next_day_note:
        st.markdown('<div class="warn-note">⚠️ Exit time is before entry — booking extends to the next day.</div>', unsafe_allow_html=True)

    # Step 2
    st.markdown("""
    <div class="step-wrap" style="margin-top:1.25rem;">
        <span class="step-num">2</span>
        <span class="step-title">Choose an available slot</span>
    </div>
    """, unsafe_allow_html=True)

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
        if st.session_state.selected_slot == slot_name:
            st.session_state.selected_slot = None
        else:
            st.session_state.selected_slot = slot_name

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
                color: var(--accent-2)!important;
                font-weight:700!important;
            }}\n"""
        elif is_blocked:
            slot_css += f"""{sel} {{
                background: var(--red-soft)!important;
                border: 1px solid rgba(239,68,68,0.15)!important;
                color: var(--red)!important;
                cursor: not-allowed!important;
                opacity:0.7!important;
            }}\n"""
        else:
            slot_css += f"""{sel} {{
                border-left: 2px solid var(--green)!important;
                color: var(--text-2)!important;
            }}\n"""
            slot_css += f"""{sel}:hover {{
                background: var(--green-soft)!important;
                border-color: var(--green)!important;
                color: var(--green)!important;
            }}\n"""

    st.markdown(f"<style>{slot_css}</style>", unsafe_allow_html=True)

    for row_prefix in ['A', 'B']:
        row_slots = [f"{row_prefix}{i}" for i in range(1, 11)]
        st.markdown(f'<div class="row-label">Row {row_prefix}</div>', unsafe_allow_html=True)
        cols = st.columns(10)
        for j, s in enumerate(row_slots):
            with cols[j]:
                is_blocked = s in blocked
                is_disabled = is_blocked or (st.session_state.selected_slot is not None and st.session_state.selected_slot != s)
                st.button(s, key=f"slot_{s}", on_click=handle_slot_click, args=(s,), disabled=is_disabled, use_container_width=True)

    if st.session_state.selected_slot:
        current_blocked = {r[0] for r in cur.execute(
            "SELECT slot_number FROM bookings WHERE NOT (end_datetime <=? OR start_datetime >=?)",
            (start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))
        ).fetchall()}

        if st.session_state.selected_slot in current_blocked:
            st.error(f"Slot {st.session_state.selected_slot} is no longer available. Please choose another.")
            st.session_state.selected_slot = None
            st.rerun()
        else:
            st.markdown(f"""
            <div class="confirm-banner">
                <div style="font-size:0.65rem;color:var(--text-3);font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:2px;">Selected</div>
                <div class="confirm-slot-big">{st.session_state.selected_slot}</div>
                <div class="confirm-time">{start_dt.strftime('%b %d · %I:%M %p')} → {end_dt.strftime('%I:%M %p')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Confirm Booking →", type="primary", use_container_width=True):
                if start_dt < now_dt_fresh_ist:
                    st.error("Your selected start time has just passed. Please pick a new time.")
                    st.session_state.selected_slot = None
                    st.rerun()
                else:
                    try:
                        cur.execute(
                            "INSERT INTO bookings (user_id, slot_number, start_datetime, end_datetime) VALUES (?,?,?,?)",
                            (st.session_state.user_id, st.session_state.selected_slot,
                             start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"))
                        )
                        conn.commit()
                        st.success(f"✅ Slot {st.session_state.selected_slot} booked successfully!")
                        st.session_state.selected_slot = None
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"Failed to book slot {st.session_state.selected_slot}. It may have just been taken.")
                        st.session_state.selected_slot = None
                        st.rerun()
    else:
        st.markdown("""
        <div class="empty-card" style="padding:1rem;margin-top:0.75rem;">
            <div class="empty-sub">Tap an available slot above to continue</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="lock-card">
        <div class="lock-icon">🔒</div>
        <div class="lock-title">Booking Locked</div>
        <div class="lock-sub">You have an active or upcoming booking.<br>Manage your existing sessions above to make a new booking.</div>
    </div>
    """, unsafe_allow_html=True)
