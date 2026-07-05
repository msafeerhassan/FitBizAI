import streamlit as st

homePage = st.Page("home.py", title="Home", default=True)
addDietPage = st.Page("pages/addDiet.py", title="Log Meal Intake", icon="🍴")
addWaterPage = st.Page("pages/addWater.py", title="Log Water Intake", icon="💧")
addWorkoutPage = st.Page("pages/addWorkout.py", title="Log Workout", icon="🏋️‍♂️")
addContextPage = st.Page("pages/addContext.py", title="Log Additional Context", icon="💬")

pg = st.navigation({
    "Main": [homePage],
    "Options": [
        addDietPage,
        addWaterPage,
        addWorkoutPage,
        addContextPage
        ]
})

pg.run()