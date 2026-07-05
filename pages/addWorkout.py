import streamlit as st
from db import saveData

with st.form(key="addWorkout", clear_on_submit=True, border=False):

    st.header("Log a Workout Performed")

    date = st.date_input("Pick a date: ", value="today")
    time = st.time_input("Pick a time: ", value="now")

    type = st.text_input("Enter Workout Type: ", placeholder="Pushups, Pullups etc")

    amount = st.number_input("Enter number: ", min_value=1, placeholder=5)

    addBtn = st.form_submit_button("Log Workout")

if addBtn:
    data = {
        "date": date.isoformat(),
        "time": time.strftime("%H:%M:%S"),
        "type": type,
        "amount": amount
    }

    saveData("workout", data)
    st.success("Workout Logged!")