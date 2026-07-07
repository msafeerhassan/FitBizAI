import streamlit as st
from db import saveUserProfile

with st.form(key="signup", border=False):
    st.header("Sign Up")

    name = st.text_input(label="Enter your name: ")
    age = st.number_input(label="Enter your age: ", min_value=13)
    height = st.number_input(label="Enter your height (cm): ", min_value=50)
    location = st.text_input(label="Enter your location", placeholder="Texas, US")

    btn = st.form_submit_button(label="Sign Up", type="primary")

if btn:
    data = {
        "name": name,
        "age": age,
        "height_in_cm": height,
        "location": location
    }

    saveUserProfile(data)

    st.success("User Profile Successfully Created! Refresh to access application.")