import streamlit as st
from db import saveData

with st.form(key="addContext", clear_on_submit=True, border=False):
    st.header("Log Additional Context")

    date = st.date_input("Enter date: ", value="today")
    time = st.time_input("Enter time: ", value="now")

    text = st.text_area("Log: ", placeholder="Today, we hosted a party so that's why I consumed a lot of soft drinks...", height="content")

    addBtn = st.form_submit_button("Log Additional Context")

if addBtn:
    data = {
        "date": date.isoformat(),
        "time": time.strftime("%H:%M:%S"),
        "text": text
    }

    saveData("context", data)
    st.success("Context Logged!")