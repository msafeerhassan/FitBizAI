import streamlit as st
import json, os
from datetime import date

FILE_PATH = "record.json"

st.set_page_config(page_title="FitBizAI - Home", page_icon="🏋️‍♂️")
st.title("FitBizAI - Dashboard")

def loadData():
    todayDateStr = date.today().isoformat()

    todaysSummary = {
        "diet": [],
        "water": 0.0,
        "workout": [],
        "context": []
    }

    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        return todaysSummary, False
    

    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)

            for item in data.get("diet", []):
                if item.get("date") == todayDateStr:
                    todaysSummary["diet"].append(item)
            
            for item in data.get("water", []):
                if item.get("date") == todayDateStr:
                    try:
                        todaysSummary["water"] += float(item.get("amount", 0))
                    except (ValueError, TypeError):
                        pass
            for item in data.get("workout", []):
                if item.get("date") == todayDateStr:
                    todaysSummary["workout"].append(item)
            for item in data.get("context", []):
                if item.get("date") == todayDateStr:
                    todaysSummary["context"].append(item)
            
            return todaysSummary, data
    except (json.JSONDecodeError, KeyError, ValueError):
        return todaysSummary, False

todayData, fullHistory = loadData()

st.subheader(f"Today's Progress - {date.today().strftime('%B %d, %Y')}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Water Intake", value=f"{todayData['water']:.2f} L")
with col2:
    st.metric(label="Meals Logged Today", value=f"{len(todayData["diet"])} meals")
with col3:
    st.metric(label="Today's Workout", value=f"{len(todayData["workout"])} sessions")

st.divider()

leftCol, rightCol = st.columns(2)

with leftCol:
    st.markdown("### Meal Log")
    if todayData["diet"]:
        for meal in todayData["diet"]:
            st.info(f"**{meal['time']}**\n\n{meal['item']}")
    else:
        st.caption("No meals logged yet today :(")
    
    st.markdown("### Additional Context")
    if todayData['context']:
        for context in todayData['context']:
            st.warning(f"**{context['time']}**\n\n{context['text']}")
    else:
        st.caption("No Additional Context Logged today :(")

with rightCol:
    st.markdown("### Workout Log")
    if todayData["workout"]:
        tableRow = []
        for i in todayData["workout"]:
            tableRow.append({
                "Time": i["time"],
                "Workout Type": i["type"],
                "Amount": i["amount"]
            })
        st.table(tableRow)
    else:
        st.caption("No Workouts Logged Today :(")
st.divider()

st.markdown("### Daily Report Compilation")

btn = st.button("Compile & Share Report with AI", type="primary")

if btn:
    if not fullHistory:
        st.error("No Record Data Found yet :(")
    else:
        st.write(todayData)