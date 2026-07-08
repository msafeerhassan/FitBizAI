import streamlit as st
import pandas as pd
from datetime import date, timedelta
import json, os

RECORD_FILE = "record.json"

st.header("FitBizAI - Insights")

daysRange = 30
weightDaysRange = 90

def loadData():

    if not os.path.exists(RECORD_FILE) or os.stat(RECORD_FILE).st_size == 0:
        return None
    
    try:
        with open(RECORD_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return None
    
def getDateRange(days):
    today = date.today()
    dateList = []

    dayOff = days - 1

    while dayOff >= 0:
        currentDay = today - timedelta(days=dayOff)
        dateList.append(currentDay)
        dayOff = dayOff - 1

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

    for isoDate in bkts:
        entries = bkts[isoDate]

        if mode == "count":
            result[isoDate] = len(entries)
        elif mode == "sum":
            total = 0.0
            for entry in entries:
                rawVal = entry.get(valueKey, 0)
                try:
                    total = total + float(rawVal)
                except (ValueError, TypeError):
                    total = total
            
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
            rows[reviewDate]["diet"] = scores.get("diet")
            rows[reviewDate]["water"] = scores.get("water")
            rows[reviewDate]["workout"] = scores.get("workout")
            rows[reviewDate]["productivity"] = scores.get("productivity")
    
    scoresDf = pd.DataFrame.from_dict(rows, orient="index")
    return scoresDf

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
    
    weightDf = pd.DataFrame.from_dict(rows, orient="index", columns=["weight"])
    weightDf = weightDf.sort_index()

    return weightDf


data = loadData()

if not data:
    st.info("No Data Recorded Yet :( Start logging to see insights here!")
    st.stop()

dateRange = getDateRange(daysRange)
weightDateRange = getDateRange(weightDaysRange)

st.markdown("### Water Intake (Litres/day)")

waterRecords = data.get("water", [])

waterData = aggrDaily(waterRecords, dateRange, valueKey="amount", mode="sum")
waterSeries = pd.Series(waterData, name="Litres")
st.line_chart(waterSeries)

st.markdown("### Workout Sessions (count/day)")

workoutRecords = data.get("workout", [])
workoutData = aggrDaily(workoutRecords, dateRange, mode="count")
workoutSeries = pd.Series(workoutData, name="Sessions")
st.bar_chart(workoutSeries)

st.markdown("### Productive Minutes Spent/day")

productivityRecord = data.get("productivity", [])
productivityData = aggrDaily(productivityRecord, dateRange, valueKey="time_spent", mode="sum")
productivitySeries = pd.Series(productivityData, name="Minutes")
st.line_chart(productivitySeries)

st.markdown("### AI Coach Scores (out of 10)")

reviewRecord = data.get("ai_reviews", [])
scoresDf = extractAIScores(reviewRecord, dateRange)

scoreCol1, scoreCol2 = st.columns(2)

with scoreCol1:
    st.markdown("#### Diet Score")
    dietSeries = scoresDf["diet"]
    st.line_chart(dietSeries)

    st.markdown("#### Workout Score")
    workoutSeries = scoresDf["workout"]
    st.line_chart(workoutSeries)

with scoreCol2:
    st.markdown("#### Water Score")
    waterScoreSeries = scoresDf["water"]
    st.line_chart(waterScoreSeries)

    st.markdown("#### Productivity Score")
    productivitySeries = scoresDf["productivity"]
    st.line_chart(productivitySeries)

st.markdown("### Weight Trend (kg's)")

fortnightlyRecors = data.get("fortnightly", [])
weightDf = extractWeight(fortnightlyRecors, weightDateRange)

if weightDf.empty:
    st.caption(f"No Fortnightly Weight Recorded :( in last {daysRange} days.")
else:
    st.line_chart(weightDf)