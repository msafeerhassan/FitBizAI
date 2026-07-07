import streamlit as st
from db import saveData

with st.form(key="addProductivity", clear_on_submit=True, border=False):
    st.header("Log Productivity and Deep-Work Sessions")

    date = st.date_input(label="Enter the date: ", value="today")
    time = st.time_input(label="Enter the time: ", value="now")

    type = st.text_input(label="Enter the type of work you did: ", placeholder="Coding, Studying...")
    timeSpent = st.number_input(label="Enter number of minutes you spent on this: ", min_value=1)

    btn = st.form_submit_button(label="Log")

if btn:
    data = {
        "date": date.isoformat(),
        "time": time.strftime("%H:%M:%S"),
        "type": type,
        "time_spent": timeSpent
    }

    saveData("productivity", data)