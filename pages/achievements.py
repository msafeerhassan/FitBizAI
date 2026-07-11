import streamlit as st
from datetime import date
from db import loadFullRecordData, loadChatHistory

st.header("Achievements")

recordData = loadFullRecordData()

if not recordData:
    st.info("No data recorded yet - Start logging data!")
    st.stop()

chatHistory = loadChatHistory()

def getLongestReportStreak(history):
    aiReviews = history.get("ai_reviews", [])
    reviewDates = set()

    for review in aiReviews:
        reviewDateStr = review.get("date")
        
        try:
            reviewDate = date.fromisoformat(reviewDateStr)
            reviewDates.add(reviewDate)
        except (ValueError, TypeError):
            continue
    
    if not reviewDates:
        return 0
    
    sortedDates = sorted(reviewDates)

    longestStreak = 1
    currentStreak = 1
    i = 1

    while i < len(sortedDates):
        prevDate = sortedDates[i - 1]
        currDate = sortedDates[i]
        dayDiff = (currDate - prevDate).days

        if dayDiff == 1:
            currentStreak = currentStreak + 1
        else:
            currentStreak = 1
        
        if currentStreak > longestStreak:
            longestStreak = currentStreak
        
        i = i + 1
    
    return longestStreak

totalWorkoutsLogged = len(recordData.get("workout", []))
totalMealsLogged = len(recordData.get("diet", []))
totalFortnightlyLogs = len(recordData.get("fortnightly", []))
totalWeeklyRecapsGen = len(recordData.get("weekly_recap", []))
totatChatsMsgWithCoach = len(chatHistory)
longestReportStreak = getLongestReportStreak(recordData)

badgeList = []

badgeList.append({
    "title": "First Check-In",
    "description": "Submit your first fortnightly report.",
    "icon": "📅",
    "earned": totalFortnightlyLogs >= 1
})

badgeList.append({
    "title": "Committed Tracker",
    "description": "Submit 3 Fortnightly Reports",
    "icon": "📅",
    "earned": totalFortnightlyLogs >= 3
})

badgeList.append({
    "title": "First Recap",
    "description": "Generate Your First Weekly Recap",
    "icon": "📝",
    "earned": totalWeeklyRecapsGen >= 1
})

badgeList.append({
    "title": "Getting Started",
    "description": "Log 10 Workouts",
    "icon": "🏋️‍♂️",
    "earned": totalWorkoutsLogged >= 10
})

badgeList.append({
    "title": "Workout Warrior",
    "description": "Log 50 Workouts",
    "icon": "💪",
    "earned": totalWorkoutsLogged >= 50
})

badgeList.append({
    "title": "Well-Fed",
    "description": "Log 100 Meals",
    "icon": "🍽️",
    "earned": totalMealsLogged >= 100
})


badgeList.append({
    "title": "One Week Strong",
    "description": "Generate a daily report 7 days in a row",
    "icon": "🔥",
    "earned": longestReportStreak >= 7
})

badgeList.append({
    "title": "One Month Strong",
    "description": "Generate a daily report 30 days in a row",
    "icon": "🌟",
    "earned": longestReportStreak >= 30
})

badgeList.append({
    "title": "Coach's Pet",
    "description": "Send your first message to the AI Coach",
    "icon": "💬",
    "earned": totatChatsMsgWithCoach >= 1
})

earnedCount = 0
for badge in badgeList:
    if badge["earned"]:
        earnedCount = earnedCount + 1

st.markdown(f"#### {earnedCount} of {len(badgeList)} Earned")

st.divider()

badgeCols = st.columns(3)
columnIndex = 0

for badge in badgeList:
    with badgeCols[columnIndex]:
        if badge["earned"]:
            st.success(f"{badge["icon"]} **{badge['title']}**\n\n{badge['description']}")
        else:
            st.caption(f"🔒 {badge['title']}\n\n{badge['description']}")
    
    columnIndex = columnIndex + 1
    if columnIndex >= 3:
        columnIndex = 0
