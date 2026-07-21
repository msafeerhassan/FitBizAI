from datetime import date
from flask import Blueprint
from db import loadFullRecordData, loadChatHistory
from layout import renderPage

achievementsBp = Blueprint("achievements", __name__)

def getLongestReportStreak(history):
    aiReviews = history.get("ai_reviews", [])
    reviewDates = set()

    for review in aiReviews:
        try:
            reviewDates.add(date.fromisoformat(review.get("date")))
        except (ValueError, TypeError):
            continue
    
    if not reviewDates:
        return 0
    
    sortedDates = sorted(reviewDates)
    longestStreak = 1
    currentStreak = 1
    i = 1

    while i < len(sortedDates):
        dayDiff = (sortedDates[i] - sortedDates [i - 1]).days

        if dayDiff == 1:
            currentStreak += 1
        else:
            currentStreak = 1
        
        if currentStreak > longestStreak:
            longestStreak = currentStreak
        
        i += 1
    
    return longestStreak

@achievementsBp.route("/achievements", methods = ["GET"])
def achievements():
    recordData = loadFullRecordData()
    if not recordData:
        return renderPage("Achievements", '<p>No Data Recorded Yet - Start Logging Data!</p>')
    
    chatHistory = loadChatHistory()

    totalWorkoutsLogged = len(recordData.get("workout", []))
    totalMealsLogged = len(recordData.get("diet", []))
    totalFortnightlyLogs = len(recordData.get("fortnightly", []))
    totalWeeklyRecapsGen = len(recordData.get("weekly_recap", []))
    totalChatMsgWithCoach = len(chatHistory)
    longestReportStreak = getLongestReportStreak(recordData)


    badgeList = [
        {
        "title": "First Check-In",
        "description": "Submit your first fortnightly report.",
        "icon": "📅",
        "earned": totalFortnightlyLogs >= 1
        },

        {
        "title": "Committed Tracker",
        "description": "Submit 3 Fortnightly Reports",
        "icon": "📅",
        "earned": totalFortnightlyLogs >= 3
        },
        {
        "title": "First Recap",
        "description": "Generate Your First Weekly Recap",
        "icon": "📝",
        "earned": totalWeeklyRecapsGen >= 1
    },
    {
        "title": "Getting Started",
        "description": "Log 10 Workouts",
        "icon": "🏋️‍♂️",
        "earned": totalWorkoutsLogged >= 10
    },
    {
        "title": "Workout Warrior",
        "description": "Log 50 Workouts",
        "icon": "💪",
        "earned": totalWorkoutsLogged >= 50
    },
    {
        "title": "Well-Fed",
        "description": "Log 100 Meals",
        "icon": "🍽️",
        "earned": totalMealsLogged >= 100
    },
    {
        "title": "One Week Strong",
        "description": "Generate a daily report 7 days in a row",
        "icon": "🔥",
        "earned": longestReportStreak >= 7
    },
    {
        "title": "One Month Strong",
        "description": "Generate a daily report 30 days in a row",
        "icon": "🌟",
        "earned": longestReportStreak >= 30
    },
    {
        "title": "Coach's Pet",
        "description": "Send your first message to the AI Coach",
        "icon": "💬",
        "earned": totalChatMsgWithCoach >= 1
    }

    ]

    earnedCount = 0

    for b in badgeList:
        if b["earned"]:
            earnedCount += 1
        

    body = f"<h2>Achievements</h2><h4>{earnedCount} of {len(badgeList)} Earned</h4><hr>"
    body += '<div style="display: flex; flex-wrap: wrap; gap: 12px;">'

    for badge in badgeList:
        if badge["earned"]:
            cls = "badge-earned"
        else:
            cls = "badge-locked"
        
        if badge["earned"]:
            icon = badge["icon"]
        else:
            icon = "🔒"
        
        body += f"""
<div class="{cls}" style="width: 200px;">
    <strong>{icon} {badge['title']}</strong>
    <p style="margin: 6px 0 0; font-size: 14px;">{badge['description']}</p>    
</div>
"""
    
    body += "</div>"

    return renderPage("Achievements", body)