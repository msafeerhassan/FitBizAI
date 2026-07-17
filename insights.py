from datetime import date, timedelta
import json
from flask import Blueprint
from db import loadUserProfile, loadFullRecordData
from layout import renderPage

insightsBp = Blueprint("insights", __name__)

daysRange = 30
weightDaysRange = 90
    
def getDateRange(days):
    today = date.today()
    dateList = []

    dayOff = days - 1

    while dayOff >= 0:
        dateList.append(today - timedelta(days=dayOff))
        dayOff -= 1

    return dateList

def aggrDaily(records, dateRange, valueKey = None, mode="sum"):
    bkts = {}

    for sinDate in dateRange:
        isoDate = sinDate.isoformat()
        bkts[isoDate] = []
    
    for record in records:
        recordDate = record.get("date")
        if recordDate in bkts:
            bkts[recordDate].append(record)
    
    result = {}

    for isoDate, entries in bkts.items():
        if mode == "count":
            result[isoDate] = len(entries)
        else:
            total = 0.0
            for entry in entries:
                try:
                    total += float(entry.get(valueKey, 0))
                except (ValueError, TypeError):
                    pass
            
            result[isoDate] = total
    return result

def extractAIScores(reviews, dateRange):
    rows = {}

    for sinDate in dateRange:
        isoDate = sinDate.isoformat()

        rows[isoDate] = {
            "diet": None,
            "water": None,
            "workout": None,
            "productivity": None
        }
    
    for review in reviews:
        reviewDate = review.get("date")
        if reviewDate in rows:
            scores = review.get("scores", {})
            rows[reviewDate] = {
                "diet": scores.get("diet"),
                "water": scores.get("water"),
                "workout": scores.get("workout"),
                "productivity": scores.get("productivity")
            }
    return rows

def extractWeight(fortnightlyLogs, dateRange):
    startDate = dateRange[0]
    endDate = dateRange[-1]

    rows = {}

    for log in fortnightlyLogs:
        logDateStr = log.get("date", "")

        try:
            logDate = date.fromisoformat(logDateStr)
        except ValueError:
            continue

        if logDate >= startDate and logDate <= endDate:
            rows[logDateStr] = log.get("weight")

    return dict(sorted(rows.items()))

@insightsBp.route("/insights", methods = ["GET"])
def insights():
    data = loadFullRecordData()

    if not data:
        return renderPage("Insights", "<p>No Data recorded yet :( Start Logging to see insights here.</p>")
    
    userProfile = loadUserProfile()

    if userProfile:
        waterTarget = userProfile.get("water_target_litres", 1.0)
        workoutTarget = userProfile.get("workout_sessions_target", 1)
        productivityTarget = userProfile.get("productivity_minutes_target", 10)
    else:
        waterTarget, workoutTarget, productivityTarget = 1.0, 1, 10
    
    dateRange = getDateRange(daysRange)

    labels = []

    for d in dateRange:
        labels.append(d.isoformat())
    
    waterData = aggrDaily(data.get("water", []), dateRange, valueKey="amount", mode="sum")
    workoutData = aggrDaily(data.get("workout", []), dateRange, mode="count")
    productivityData = aggrDaily(data.get("productivity", []), dateRange, valueKey="time_spent", mode="sum")
    scoresData = extractAIScores(data.get("ai_reviews", []), dateRange)

    weightDateRange = getDateRange(weightDaysRange)

    weightRows = extractWeight(data.get("fortnightly", []), weightDateRange)

    water = []
    workout = []
    productivity = []
    dietScore = []
    waterScore = []
    workoutScore = []
    productivityScore = []

    for d in labels:
        water.append(waterData[d])
        workout.append(workoutData[d])
        productivity.append(productivityData[d])

        dayScores = scoresData[d]
        dietScore.append(dayScores["diet"])
        waterScore.append(dayScores["water"])
        workoutScore.append(dayScores["workout"])
        productivityScore.append(dayScores["productivity"])
    
    weightLabels = []
    weightVals = []

    for key, value in weightRows.items():
        weightLabels.append(key)
        weightVals.append(value)
    
    chartData = {
        "labels": labels,
        "water": water,
        "waterTarget": waterTarget,
        "workout":workout,
        "workoutTarget" : workoutTarget,
        "productivity": productivity,
        "productivityTarget": productivityTarget,
        "dietScore": dietScore,
        "waterScore": waterScore,
        "workoutScore": workoutScore,
        "productivityScore": productivityScore,
        "weightLabels": weightLabels,
        "weightValues": weightVals
    }

    body = f"""
<h2>Insights</h2>
<div class="card"><h4>Water Intake (Litres/day)</h4><canvas id="waterChart"></canvas></div>
<div class="card"><h4>Workout Sessions (count/day)</h4><canvas id="workoutChart"></canvas></div>
<div class="card"><h4>Productive Minutes Spent/day</h4><canvas id="productivityChart"></canvas></div>
<div class="card"><h4>AI Coach Scores (out of 10)</h4><canvas id="scoresChart"></canvas></div>
<div class="card"><h4>Weight Trend (kg's)</h4></div>
"""
    
    if not weightRows:
        body += f"<p class=\"caption\">No Fortnightly Weight Recorded in last {daysRange} days.</p></div>"
    else:
        body += '<canvas id="weightChart"></canvas></div>'
    
    body += f"""
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>

const data = {
    json.dumps(chartData)
};

function lineChart(id, labels, datasets) {{
    new Chart(document.getElementById(id), {{
        type: "line",
        data: {{
            labels,
            datasets
        }}
    }});
}}

lineChart("waterChart", data.labels, [
    {{
        label: "Actual (L)", data: data.water, borderColor: "#2563eb"
    }},
    {{
        label: "Target (L)", data: data.labels.map(() => data.waterTarget), borderColor: "#999", borderDash: [5,5]
    }}
]);

lineChart("workoutChart", data.labels, [
    {{
        label: "Actual Sessions", data: data.workout, borderColor: "#16a34a"
    }},
    {{
        label: "Target Sessions", data: data.labels.map(() => data.workoutTarget), borderColor: "#999", borderDash: [5,5]
    }}
]);

lineChart("productivityChart", data.labels, [
    {{
        label: "Actual (min)", data: data.productivity, borderColor: "#d97706"
    }},
    {{
        label: "Target (min)", data: data.labels.map(() => data.productivityTarget), borderColor: "#999", borderDash: [5,5]
    }}
]);

lineChart("scoresChart", data.labels, [
    {{
        label: "Diet", data: data.dietScore, borderColor: "#ef4444"
    }},
    {{
        label: "Water", data: data.waterScore, borderColor: "#2563eb"
    }},
    {{
        label: "Workout", data: data.workoutScore, borderColor: "#16a34a"
    }},
    {{
        label: "Productivity", data: data.productivityScore, borderColor: "#d97706"
    }}
]);

if (data.weightLabels.length) {{
    lineChart("weightChart", data.weightLabels, [
        {{
            label: "Weight (kg)",
            data: data.weightValues,
            borderColor: "#7c3aed"
        }}
    ]);
}}
</script>
"""

    return renderPage("Insights", body)