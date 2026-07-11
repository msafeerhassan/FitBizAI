import streamlit as st
import os, json
from datetime import datetime, date

FILE_PATH = "record.json"
USER_PROFILE_PATH = "userProfile.json"

def fortnightCheck():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        return True
    
    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
            fortnighlyLogs = data.get("fortnightly", [])

            if not fortnighlyLogs:
                return True
            
            lastLogStr = fortnighlyLogs[-1].get("date")
            lastLogDate = datetime.strptime(lastLogStr, "%Y-%m-%d").date()

            daysPassed = (date.today() - lastLogDate).days

            return daysPassed >= 14
    except (json.JSONDecodeError, KeyError, ValueError):
        return True

def existingUserCheck():
    if not os.path.exists(USER_PROFILE_PATH) or os.stat(USER_PROFILE_PATH).st_size == 0:
        return False
    else:
        return True

homePage = st.Page("home.py", title="Home", default=True, icon="🏠")
addDietPage = st.Page("pages/addDiet.py", title="Log Meal Intake", icon="🍴")
addWaterPage = st.Page("pages/addWater.py", title="Log Water Intake", icon="💧")
addWorkoutPage = st.Page("pages/addWorkout.py", title="Log Workout", icon="🏋️‍♂️")
addContextPage = st.Page("pages/addContext.py", title="Log Additional Context", icon="💬")
fortnightlyLogPage = st.Page("pages/fortnightlyLog.py", title="Mandatory Fortnightly Report", icon="🗓️")
productivityLogPage = st.Page("pages/addProductivity.py", title="Log Work", icon="🕧")
signupPage = st.Page("signup.py", title="Sign Up", icon="🪧")
insightsPage = st.Page("insights.py", title="Insights", icon="📊")
coachChatPage = st.Page("pages/coachChat.py", title="Chat with Coach", icon="🤖")
manageLogsPage = st.Page("pages/manageLogs.py", title="Manage your Logs", icon="📒")
targetsPage = st.Page("pages/targets.py", title="Manage Targets", icon="🎯")
progressPhotosPage = st.Page("pages/progressPhotos.py", title="Progress Photos", icon="🖼️")
achievementsPage = st.Page("pages/achievements.py", title="Achievements", icon="🏆")

if existingUserCheck():
    if fortnightCheck():
        fortnightlyLogPage.default = True
        pg = st.navigation({
            "Action Required": [fortnightlyLogPage]
        })

    else:
        pg = st.navigation({
            "Main": [
                homePage,
                insightsPage,
                achievementsPage
            ],
            "Options": [
                manageLogsPage,
                targetsPage,
                progressPhotosPage,
                addDietPage,
                addWaterPage,
                addWorkoutPage,
                addContextPage,
                productivityLogPage,
                coachChatPage
                ]
        })
else:
    signupPage.default = True
    pg = st.navigation({
        "Action Required": [signupPage]
    })

pg.run()