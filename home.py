import streamlit as st
import json, os
from datetime import date
import datetime
from ai import runAIdaily
from db import saveData

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
        todayDate = date.today()
        fourteenDaysAgo = todayDate - datetime.timedelta(days=14)

        slicedHistory = {
            "diet": [],
            "water": [],
            "workout": [],
            "context": [],
            "ai_reviews": []
        }

        for category in ["diet", "water", "workout", "context", "ai_reviews"]:
            for item in fullHistory.get(category, []):
                try:
                    itemDate = datetime.date.fromisoformat(item.get("date", ""))
                    if fourteenDaysAgo <= itemDate < todayDate:
                        slicedHistory[category].append(item)
                except ValueError:
                    continue
        
        todayStr = todayDate.isoformat()
        todayImages = []
        currentWeight = "Not Reported Today"

        for checkin in fullHistory.get("fortnightly", []):
            if checkin.get("date") == todayStr:
                todayImages = checkin.get("image_paths", [])
                currentWeight = f"{checkin.get('weight')} kg"
                break
        
        SYSTEM_PROMPT = """You are a highly specialized Health and Fitness Coach. You will evaluate Today's logs alongside a 14-day history baseline containing raw metric inputs and previous AI analysis reviews.

                        CRITICAL COACHING OBJECTIVES:
                        1. Consistency Baseline: Prioritize deliberate habit formation and routine maintenance over intensity. If routine workouts are explicitly low-friction (e.g. 5 pushups) to guarantee long-term discipline, score it highly for execution. 
                        2. Direct Context Consideration: Prioritize reading the "Additional Context" parameters before reducing performance points. If nutrition deviations or lower outputs are clearly justified, adjust guidance constructively.
                        3. Review Historical Continuity: Read through the "ai_reviews" list from previous days. Evaluate if the user is following your yesterday recommendations or if patterns are breaking down.
                        4. Vision Progress Tracking (When Present): If facial progress pictures are attached to the payload, perform a technical look at physical muscle tones, skin clarity changes, puffiness levels, and biometric symmetry variations relative to the stated body weight. Provide structural adjustments for the next bi-weekly block.

                        Your response MUST be a valid JSON object matching this exact structure, with no markdown code block backticks around it:
                        {
                            "analysis": {
                                "positives": ["list of positive observations regarding consistency or communication"],
                                "negatives": ["list of constructive areas needing attention or improvement"],
                                "tomorrow_goals": ["1-2 hyper-specific, sustainable actions for tomorrow"]
                            },
                            "scores": {
                                "diet": 0.0,
                                "water": 0.0,
                                "workout": 0.0
                            }
                        }"""
        
        USER_PROMPT = f"""
                    Here is the complete configuration dataset for evaluation:

                    TODAY'S METRICS:
                    - Date: {todayStr}
                    - Current Weight: {currentWeight}
                    - Water Intake volume: {todayData['water']:.2f} Litres
                    - Meals logged: {json.dumps(todayData['diet'], indent=2)}
                    - Workouts performed: {json.dumps(todayData['workout'], indent=2)}
                    - Additional Log Context: {json.dumps(todayData['context'], indent=2)}
                    - Vision Assets Attached: {"Yes, 3 images provided" if todayImages else "No, this is a normal tracking day"}

                    PREVIOUS 14-DAY PERFORMANCE HISTORY:
                    {json.dumps(slicedHistory, indent=2)}
                    """

        with st.spinner("Analyzing your today's progress..."):
            try:
                response = runAIdaily(SYSTEM_PROMPT, USER_PROMPT, imagePaths=todayImages)

                if response:
                    st.success("AI Coach Analysis Complete!")

                    historicalData = {
                        "date": todayStr,
                        "scores": response.get("scores", {}),
                        "summary_goals": response.get("analysis", {}).get("tomorrow_goals", [])
                    }

                    saveData("ai_reviews", historicalData)

                    st.markdown("### Today's Performance Scores")
                    scores = response.get("scores", {})

                    scCol1, scCol2, scCol3 = st.columns(3)

                    with scCol1:
                        st.metric("Diet Score", f"{scores.get('diet', 0.0)}/10")
                    with scCol2:
                        st.metric("Water Score", f"{scores.get("water", 0.0)}/10")
                    with scCol3:
                        st.metric("Workout Score", f"{scores.get("workout", 0.0)}/10")
                    
                    st.divider()

                    analysis = response.get("analysis", {})
                    posCol, negCol = st.columns(2)

                    with posCol:
                        st.markdown("#### Positive Aspects")
                        positives = analysis.get("positives", [])
                        if positives:
                            for item in positives:
                                st.write(item)
                        else:
                            st.caption("Situation is serious. Please do something positive first :)")
                    
                    with negCol:
                        st.markdown("#### Alerts")
                        negatives = analysis.get("negatives", [])

                        if negatives:
                            for item in negatives:
                                st.write(item)
                        else:
                            st.caption("You are doing everything great :)")
                    
                    st.divider()

                    st.markdown("#### Targets for Tommorow")

                    goals = analysis.get("tomorrow_goals", [])

                    if goals:
                        for goal in goals:
                            st.info(goal)
                    else:
                        st.caption("Maintain current trajectory - nothing else required!")
                else:
                    st.error("AI Response Failed :(")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")