import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Appointment Manager")

st.title("📅 Simple Appointment Manager")

if "appointments" not in st.session_state:
    st.session_state.appointments = []

st.subheader("Add Appointment")

with st.form("appointment_form", clear_on_submit=True):
    title = st.text_input("Title")
    app_date = st.date_input("Date", min_value=date.today())
    app_time = st.time_input("Time")
    description = st.text_area("Description")

    submit = st.form_submit_button("Add")

    if submit:
        if title.strip() == "":
            st.error("Title is required")
        else:
            st.session_state.appointments.append({
                "Title": title,
                "Date": app_date,
                "Time": app_time,
                "Description": description
            })
            st.success("Appointment added")

st.subheader("Appointments")

if not st.session_state.appointments:
    st.info("No appointments yet")
else:
    df = pd.DataFrame(st.session_state.appointments)
    df = df.sort_values(by=["Date", "Time"])
    st.dataframe(df)
