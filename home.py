import streamlit as st
import json, os
from datetime import date
import datetime
from ai import runAIdaily

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
            "fortnightly": fullHistory.get("fortnightly", [])
        }

        for category in ["diet", "water", "workout", "context"]:
            for item in fullHistory.get(category, []):
                try:
                    itemDate = datetime.date.fromisoformat(item.get("date", ""))
                    if fourteenDaysAgo <= itemDate < todayDate:
                        slicedHistory[category].append(item)
                except ValueError:
                    continue
        
        SYSTEM_PROMPT = """You are a highly specialized Health and Fitness Coach. You will be given two data points: Today's Logs and Previous Records (limited to the last 14 days). Your core objective is to deeply analyze today's logs from a sustainable habit-building perspective, keeping visible historical trends in mind. 

        CRITICAL LOGIC RULES:
        1. Sustainable Habit-Formation: Prioritize consistency over intense, abrupt changes. If a workout routine is deliberately kept small and low-friction (e.g., exactly 5 pushups) to guarantee long-term adherence, evaluate it positively for discipline and form, rather than docking points for low intensity.
        2. Context Consideration: Always check the "Additional Context" field before grading. If the user eats junk food, drinks soft drinks, or experiences a deviation but clearly documents the reasons in the context log, adapt your feedback constructively. Do not aggressively penalize scores if deviations are explicitly explained or treated as part of a balanced, sustainable routine.
        3. Constructive Goals: Point out explicit improvements or degradations relative to the past 14 days, and provide actionable, small recommendations for tomorrow.

        Your response MUST be a valid JSON object matching this exact keys structure, with no markdown formatting or backticks around it:
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
        
        USER_PROMPT = f""" Here is the current tracking data to evaluate:
        TODAY'S LOGS:
        - Water Intake: {todayData['water']:.2f} Litres
        - Meals Consumed: {json.dumps(todayData['diet'], indent=2)}
        - Workouts Executed: {json.dumps(todayData['workout'], indent=2)}
        - Additional Log Context (Read this for exceptions/explanations): {json.dumps(todayData['context'], indent=2)}
        PREVIOUS 14-DAY HISTORY (FOR BENCHMARKING):
        {json.dumps(slicedHistory, indent=2)}
        """

        with st.spinner("Analyzing your today's progress..."):
            try:
                response = runAIdaily(SYSTEM_PROMPT, USER_PROMPT)

                if response:
                    st.success("AI Coach Analysis Complete!")

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