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
    font-size: 3rem;
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
(--text-1    color: var)!important;
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
    margin:
