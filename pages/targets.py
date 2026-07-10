import streamlit as st
from db import loadUserProfile, saveUserProfile

st.header("Goals & Targets")

userProfile = loadUserProfile()

if not userProfile:
    st.info("No user profile found - sign up first please.")
    st.stop()

waterTarget = userProfile.get("water_target_litres", 1)
workoutTarget = userProfile.get("workout_sessions_target", 1)
productivityTarget = userProfile.get("productivity_minutes_target", 10)

with st.form(key="editTargetsForm", border=False):
    st.markdown("### Daily Targets")

    newWaterTarget = st.number_input("Water Target (Litres/day): ", min_value=0.1, value=float(waterTarget))
    newWorkoutTarget = st.number_input("Workout Sessions Target (per day): ", min_value=1, value=int(workoutTarget))
    newProductivityTarget = st.number_input("Productivity Target (minutes/day): ", min_value=1, value=int(productivityTarget))

    saveBtn = st.form_submit_button("Save Targets", type="primary")

if saveBtn:
    userProfile["water_target_litres"] = newWaterTarget
    userProfile["workout_sessions_target"] = newWorkoutTarget
    userProfile["productivity_minutes_target"] = newProductivityTarget

    saveUserProfile(userProfile)
    st.success("Targets Updated!")