import streamlit as st

with st.form(key="addDiet", clear_on_submit=True, border=False):
    st.header("Log a consumed diet")

    date = st.date_input("Pick a date: ", value="today")
    time = st.time_input("Pick a time: ", value="now")

    item = st.text_area("What did you consumed:", placeholder="20 Almonds\n5 Protein Bars...", height="content")

    addBtn = st.form_submit_button("Log Meal")