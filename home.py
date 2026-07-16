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

@homeBp.route("/", methods=["GET"])
def home():
    history = loadFullRecordData()
    profile = loadUserProfile()

    if not profile:
        return renderPage("Home", '<p>No profile Found. <a href="/signup">Sign Up First</a>.</p>')
    
    waterTarget = profile.get("water_target_litres", 1.0)
    workoutTarget = profile.get("workout_sessions_target", 1)
    productivityTarget = profile.get("productivity_minutes_target", 10)

    today = todaySummary(history)
    streak = calculateStreak(history)
    waterStreak = calculateGoalStreak(history, "water", waterTarget, valueKey="amount", mode="sum")
    workoutStreak = calculateGoalStreak(history, "workout", workoutTarget, mode="count")
    productivityStreak = calculateGoalStreak(history, "productivity", productivityTarget, valueKey="time_spent", mode="sum")

    body = f"""
<h2>FitBizAI</h2>
<div class="card">
{renderMetric("Reporting Streak", f"{streak} days")}
{renderMetric("Water Streak", f"{waterStreak} days")}
{renderMetric("Workout Streak", f"{workoutStreak} days")}
{renderMetric("Productivity Streak", f"{productivityStreak} days")}
</div>
<div class="card">
    {renderMetric("Water Today", f"{today['water']:.2f} / {waterTarget} L")}
    {renderMetric("Meals Logged", len(today['diet']))}
    {renderMetric("Workouts", len(today['workout']))}
    {renderMetric("Productive Minutes Spent", f"{today['productivity']:.0f} / {productivityTarget}")}
</div>
<div class="card"><h4>Meal Log</h4>
"""
    
    if today["diet"]:
        for meal in today["diet"]:
            body += f"<p><strong>{meal.get('time')}</strong> - {meal.get("item")}</p>"
    else:
        body += "<p>No meals logged today yet :(</p>"
    
    body += "</div></div class=\"card\"><h4>Workout Log</h4>"

    if today["workout"]:
        for w in today["workout"]:
            body += f"<p><strong>{w.get('time')}</strong> - {w.get("type")} ({w.get('amount')})</p>"
    else:
        body += "<p>No workout sessions logged today yet :(</p>"

    body += "</div></div class=\"card\"><h4>Additional Context</h4>"

    if today["context"]:
        for c in today["context"]:
            body += f"<p><strong>{c.get('time')}</strong> - {c.get("text")}</p>"
    else:
        body += "<p>No workout sessions logged today yet :(</p>"
    
    body += "</div>"

    body += "<h3>Daily Report Compilation</h3>"

    existingReview = todayReviewExist(history)

    if existingReview:
        body += "<p>You have already generated today\'s report. Come back tomorrow.</p>"
        body += renderReviewBody(existingReview)
    else:
        body += '''
<div class="card">
    <button onclick="generateReport()">Compile & Share Report with AI</button>
    <div id="report-result"></div>
</div>
<script>
    async function generateReport() {
        document.getElementById("report-result").innerHTML = "Analyzing...";
        const res = await fetch("/generate-report", {
            method: "POST"
        });
        const data = await res.json();
        if (data.error) {
            document.getElementById("report-result").innerHTML = "Error: " + data.error;
        }
        else {
            location.reload();
        }
    }
</script>
'''
    body += "<h3>Weekly Recap</h3>"

    weeklyRecaps = (history or {}).get("weekly_recap", [])

    if weeklyRecaps:
        body += renderWeeklyRecap(weeklyRecaps[-1])
    else:
        body += "<p>No weekly recap generated yet :(</p>"
    
    if weeklyRecapCheck(history):
        body += '''
    <div class="card">
    <button onclick="generateRecap()">Generate Weekly Recap</button>
    <div id="recap-result"></div>
</div>
<script>
    async function generateRecap() {
        document.getElementById("recap-result").innerHTML = "Compiling...";
        const res = await fetch("/generate-weekly-recap", {
            method: "POST"
        });
        const data = await res.json();

        if (data.error) {
            document.getElementById("recap-result").innerHTML = "Error: " + data.error;
        }
        else {
            location.reload();
        }
    }
</script>
'''
    else:
        body += "<p>Your next weekly recap will be available once the current week is over :)</p>"

    return renderPage("Home", body)

@homeBp.route("/generate-report", methods= ["POST"])
def generateReport():
    history = loadFullRecordData()
    profile = loadUserProfile()

    if not history:
        return jsonify(
            {
                "error": "No record data found yet :("
            }
        ), 400
    
    today = todaySummary(history)
    todayDate = date.today()
    forteenDaysAgo = todayDate - timedelta(days=14)

    slicedHistory = {
        "diet": [],
        "water": [],
        "workout": [],
        "context": [],
        "productivity": [],
        "ai_reviews": []
    }

    for category in slicedHistory:
        for item in history.get(category, []):
            itemDate = date.fromisoformat(item.get("date", ""))

            if forteenDaysAgo <= itemDate < todayDate:
                slicedHistory[category].append(item)

    todayStr = todayDate.isoformat()

    todayImages = []

    currentWeight = "Not Reported Today"

    for checkin in history.get("fortnightly", []):
        if checkin.get("date") == todayStr:
            todayImages = checkin.get("image_paths", [])
            currentWeight = f"{checkin.get("weight")} kg"
            break
    
    yesterdayGoals = getYesterdayGoals(history)

    USER_PROMPT = f"""
Here is the complete configuration dataset for evaluation:

GOALS SET FOR TODAY (from yesterday's report): {yesterdayGoals if yesterdayGoals else "No goals were set yesterday - either this is a new user or yesterday's report was skipped :(."}

TODAY'S METRICS:
- Date: {todayStr}
- Current Weight: {currentWeight}
- Water Intake volume: {today['water']:.2f} Litres
- Meals logged: {today['diet']}
- Workouts performed: {today['workout']}
- Additional Log Context: {today['context']}
- Vision Assets Attached: {"Yes, " + str(len(todayImages)) + " images provided" if todayImages else "No, this is a normal tracking day"}
- Productivity: {today['productivity']}

PREVIOUS 14-DAY PERFORMANCE HISTORY:
{slicedHistory}

General User information: {profile}
"""
    try:
        response = runAIdaily(DAILY_SYSTEM_PROMPT, USER_PROMPT, imagePaths=todayImages)

        reviewData = {
            "date": todayStr,
            "scores": response.get("scores", {}),
            "analysis": response.get("analysis", {}),
            "goal_review": response.get("goal_review", {})
        }

        saveData("ai_reviews", reviewData)
        return jsonify(
            {
                "ok": True
            }
        )
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), 500

@homeBp.route("/generate-weekly-recap", methods=["POST"])
def generateWeeklyRecap():
    history = loadFullRecordData()
    if not history:
        return jsonify(
            {
                "error": "No record data found yet :("
            }
        ), 400
    
    today = date.today()

    sevenDaysAgo = today - timedelta(days=7)

    slicedWeek = {
        "diet": [],
        "water": [],
        "workout": [],
        "context": [],
        "productivity": []
    }

    for category in slicedWeek:
        for item in history.get(category, []):
            itemDate = date.fromisoformat(item.get("date", ""))

            if sevenDaysAgo <= itemDate < today:
                slicedWeek[category].append(item)
    USER_PROMPT_WEEKLY = f"""
Here is the user's data for the past seven days: {slicedWeek}
"""
    
    try:
        response = runAIdaily(WEEKLY_SYSTEM_PROMPT, USER_PROMPT_WEEKLY)

        recapData = {
            "date": today.isoformat(),
            "weekly_summary": response.get("weekly_summary", ""),
            "achievements": response.get("achievements", []),
            "areas_to_improve": response.get("areas_to_improve", []),
            "next_week_focus": response.get("next_week_focus", [])
        }

        saveData("weekly_recap", recapData)

        return jsonify(
            {
                "ok": True
            }
        )
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), 500