import streamlit as st

with st.form(key="addWater", clear_on_submit=True, border=False):
    st.header("Log water intake")

    date = st.date_input("Pick a date: ", value="today")
    time = st.time_input("Pick a time: ", value="now")

    amount = st.number_input("Enter water amount consumed (in Litres): ", min_value=0.01, placeholder=0.5)

    addBtn = st.form_submit_button("Log Water Intake")
    