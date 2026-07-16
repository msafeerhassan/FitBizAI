from flask import Blueprint, jsonify
from ai import runAIdaily
from db import saveData, loadUserProfile, loadFullRecordData
from layout import renderPage
from datetime import date,timedelta

homeBp = Blueprint("home", __name__)

def todaySummary(history):
    todayStr = date.today().isoformat()

    summary = {
        "diet": [],
        "water": 0.0,
        "workout": [],
        "context": [],
        "productivity": 0.0
    }

    if not history:
        return summary
    for item in history.get("diet", []):
        if item.get("date") == todayStr:
            summary["diet"].append(item)
    
    for item in history.get("water", []):
        if item.get("date") == todayStr:
            summary["water"] += float(item.get("amount", 0))
    
    for item in history.get("workout", []):
        if item.get("date") == todayStr:
            summary["workout"].append(item)
    for item in history.get("context", []):
        if item.get("date") == todayStr:
            summary["context"].append(item)
    for item in history.get("productivity", []):
        if item.get("date") == todayStr:
            summary["productivity"] += float(item.get("time_spent", 0))
    
    return summary

def calculateStreak(history):
    if not history:
        return 0
    
    reviewDates = set()
    for review in history.get("ai_reviews", []):
        try:
            reviewDates.add(date.fromisoformat(review.get("date")))
        except (ValueError, TypeError):
            continue
    
    if not reviewDates:
        return 0
    
    checkDate = date.today()

    if checkDate not in reviewDates:
        checkDate -= timedelta(days=1)
        if checkDate not in reviewDates:
            return 0

    streak = 0

    while checkDate in reviewDates:
        streak += 1
        checkDate -= timedelta(days=1)
    
    return streak

def getDayTotal(history, category, checkDate, valueKey=None, mode="sum"):
    if not history:
        return 0.0
    
    checkDateStr = checkDate.isoformat()
    records = history.get(category, [])

    if mode == "count":
        count = 0
        for r in records:
            if r.get("date") == checkDateStr:
                count += 1
        
        return count
    total = 0.0

    for r in records:
        if r.get("date") == checkDateStr:
            total += float(r.get(valueKey, 0))
    
    return total

def calculateGoalStreak(history, category, targetVal, valueKey=None, mode="sum"):
    if not history:
        return 0
    
    checkDate = date.today()
    todayTotal = getDayTotal(history, category, checkDate, valueKey, mode)

    if todayTotal < targetVal:
        checkDate -= timedelta(days=1)

        if getDayTotal(history, category, checkDate, valueKey, mode) < targetVal:
            return 0
    
    streak = 0

    while getDayTotal(history, category, checkDate, valueKey, mode) >= targetVal:
        streak += 1
        checkDate -= timedelta(days=1)
    return streak

def todayReviewExist(history):
    todayStr = date.today().isoformat()

    if not history:
        return None
    
    for review in history.get("ai_reviews", []):
        if review.get("date") == todayStr:
            return review
    
    return None

def getYesterdayGoals(history):
    if not history:
        return []
    
    yesterdayStr = (date.today() - timedelta(days=1)).isoformat()

    for review in history.get("ai_reviews", []):
        if review.get("date") == yesterdayStr:
            return review.get("analysis", {}).get("tomorrow_goals", [])
    
    return []

def earliestLogDate(history):
    if not history:
        return None
    earliest = None

    for category in ["diet", "water", "workout", "context", "productivity"]:
        for item in history.get(category, []):
            itemDate = date.fromisoformat(item.get("date", ""))

            if earliest is None or itemDate < earliest:
                earliest = itemDate
    
    return earliest

def weeklyRecapCheck(history):
    if not history:
        return False
    
    earliest = earliestLogDate(history)

    if earliest is None:
        return False
    
    today = date.today()

    recaps = history.get("weekly_recap", [])

    if not recaps:
        return (today - earliest).days >= 7
    
    try:
        lastRecapDate = date.fromisoformat(recaps[-1].get("date"))
    except (ValueError, TypeError):
        return False
    
    return (today - lastRecapDate).days >= 7

DAILY_SYSTEM_PROMPT = """You are a highly specialized Health and Fitness Coach. You will evaluate Today's logs alongside a 14-day history baseline containing raw metric inputs and previous AI analysis reviews.

CRITICAL COACHING OBJECTIVES:
1. Consistency Baseline: Prioritize deliberate habit formation and routine maintenance over intensity. If routine workouts are explicitly low-friction (e.g. 5 pushups) to guarantee long-term discipline, score it highly for execution.
2. Direct Context Consideration: Prioritize reading the "Additional Context" parameters before reducing performance points. If nutrition deviations or lower outputs are clearly justified, adjust guidance constructively.
3. Review Historical Continuity: Read through the "ai_reviews" list from previous days. Evaluate if the user is following your yesterday recommendations or if patterns are breaking down.
4. Vision Progress Tracking (When Present): If facial progress pictures are attached to the payload, perform a technical look at physical muscle tones, skin clarity changes, puffiness levels, and biometric symmetry variations relative to the stated body weight. Provide structural adjustments for the next bi-weekly block.
5. Weight and progress photos are only collected every 14 days as part of the fortnightly report, not daily. If "Current Weight" shows "Not Reported Today", this is completely normal and expected - do NOT comment on it or ask user to log it or treat it as missed task. Only reference weight/vision data on days its Available and present.
6. You will be given the specific goals you set for the user yesterday. Directly and honestly evaluate, using today's logged data, whether each of the goal was fulfilled, partially met or missed. Be specific and reference the actual number/logs - don't give vague praise or vague criticism.
Your response MUST be a valid JSON object matching this exact structure, with no markdown code block backticks around it:
{
    "analysis": {
        "positives": ["list of positive observations regarding consistency or communication"],
        "negatives": ["list of constructive areas needing attention or improvement"],
        "tomorrow_goals": ["1-2 hyper-specific, sustainable actions for tomorrow"]
    },
    "goal_review": {
        "had_goals_yesterday": true,
        "verdict": ["one entry per goal from yesterday, stating whether it was met, partially met or missed with a short reasoning."]
    },
    "scores": {
        "diet": 0.0,
        "water": 0.0,
        "workout": 0.0,
        "productivity": 0.0
    }
}"""

WEEKLY_SYSTEM_PROMPT = """You are a health and fitness coach writing a weekly recap based on user's last 7 days of logs.

Your response MUST be a valid JSON object matching this exact structure, with no markdown code block backticks etc:
{
    "weekly_summary": "a short 2-3 sentence overview of how this week went overall",
    "achievements": ["list of specific things the user did well this week"],
    "areas_to_improve": ["list of specific, constructive areas needing attention"],
    "next_week_focus": ["1-3 specific, achievable goals for next week"]
}"""

def renderMetric(label, value):
    return f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>'

def renderScores(scores):
    html = '<div class="card"><h3>Scores</h3>'
    html += renderMetric("Diet", f"{scores.get("diet", 0)}/10")
    html += renderMetric("Water", f"{scores.get("water", 0)}/10")
    html += renderMetric("Workout", f"{scores.get("workout", 0)}/10")
    html += renderMetric("Productivity", f"{scores.get("productivity", 0)}/10")
    return html + "</div>"

def renderReviewBody(review):
    scores = review.get("scores", {})
    analysis = review.get("analysis", {})
    goalReview = review.get("goal_review", {})

    html = renderScores(scores)

    if goalReview.get("had_goals_yesterday"):
        html += '<div class="card"><h4>Yesterday\'s Goals</h4><ul>'

        for v in goalReview.get("verdict", []):
            html += f"<li>{v}</li>"
        
        html += "</ul></div>"
    
    html += '<div class="card"><h4>Positives</h4><ul>'

    for p in analysis.get("positives"):
        html += f"<li>{p}</li>"
    
    html += '</ul><h4>Alerts</h4><ul>'

    for n in analysis.get("negatives"):
        html += f"<li>{n}</li>"
    
    html += '</ul><h4>Targets for Tomorrow</h4><ul>'

    for g in analysis.get("tomorrow_goals"):
        html += f"<li>{g}</li>"
    
    html += "</ul></div>"

    return html

def renderWeeklyRecap(recap):
    html = f'<div class="card"><strong>Latest Weekly Recap - {recap.get("date")}</strong><p>{recap.get("weekly_summary", "")}</p>'

    if recap.get("achievements"):
        items = "</li><li>".join(recap["achievements"])
        html += f"<h4>Achievements</h4><ul><li>{items}</li></ul>"
    
    if recap.get("areas_to_improve"):
        items = "</li><li>".join(recap["areas_to_improve"])
        html += f"<h4>Areas to Improve</h4><ul><li>{items}</li></ul>"

    if recap.get("next_week_focus"):
        items = "</li><li>".join(recap["next_week_focus"])
        html += f"<h4>Next Week's Focus</h4><ul><li>{items}</li></ul>"
    
    return html + "</div>"

