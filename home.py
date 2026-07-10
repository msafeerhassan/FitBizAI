import streamlit as st
import json, os
from datetime import date
import datetime
from ai import runAIdaily
from db import saveData, loadUserProfile

FILE_PATH = "record.json"
USER_PROFILE_PATH = "userProfile.json"

st.set_page_config(page_title="FitBizAI - Home", page_icon="🏋️‍♂️")
st.title("FitBizAI - Dashboard")

def loadData():
    todayDateStr = date.today().isoformat()

    todaysSummary = {
        "diet": [],
        "water": 0.0,
        "workout": [],
        "context": [],
        "productivity": 0.0,
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
                
            for item in data.get("productivity", []):
                if item.get("date") == todayDateStr:
                    try:
                        todaysSummary["productivity"] += float(item.get("time_spent", 0))
                    except (ValueError, TypeError):
                        pass
            
            return todaysSummary, data
    except (json.JSONDecodeError, KeyError, ValueError):
        return todaysSummary, False

def calculateStreak(history):
    if not history:
        return 0
    
    aiReviews = history.get("ai_reviews", [])
    reviewDates = set()

    for review in aiReviews:
        reviewDateStr = review.get("date")
        try:
            reviewDate = datetime.date.fromisoformat(reviewDateStr)
            reviewDates.add(reviewDate)
        except (ValueError, TypeError):
            continue
    if not reviewDates:
        return 0
    
    checkDate = date.today()

    if checkDate not in reviewDates:
        checkDate = checkDate - datetime.timedelta(days=1)
        if checkDate not in reviewDates:
            return 0
    
    streakCount = 0

    while checkDate in reviewDates:
        streakCount = streakCount + 1
        checkDate = checkDate - datetime.timedelta(days=1)
    
    return streakCount

todayData, fullHistory = loadData()

userProfile = loadUserProfile()

if userProfile:
    waterTarget = userProfile.get("water_target_litres", 1.0)
    workoutTarget = userProfile.get("workout_sessions_target", 1)
    productivityTarget = userProfile.get("productivity_minutes_target", 10)
else:
    waterTarget = 1
    workoutTarget = 1
    productivityTarget = 10

currentStreak = calculateStreak(fullHistory)

if currentStreak == 1:
    streakLabel = "1 day"
else:
    streakLabel = f"{currentStreak} days"

st.metric("🔥 Daily Reporting Streak", value=streakLabel)

st.divider()

st.subheader(f"Today's Progress - {date.today().strftime('%B %d, %Y')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    waterDelta = todayData["water"] - waterTarget
    st.metric(label="Total Water Intake", value=f"{todayData['water']:.2f} L", delta=f"{waterDelta:.2f}L (Target: {waterTarget}L)")
with col2:
    st.metric(label="Meals Logged Today", value=f"{len(todayData["diet"])} meals")
with col3:
    workoutCount = len(todayData["workout"])
    workoutDelta = workoutCount - workoutTarget
    st.metric(label="Today's Workout", value=f"{workoutCount} sessions", delta=f"{workoutDelta} (Target: {workoutTarget} Sessions)")
with col4:
    productivityDelta = todayData["productivity"] - productivityTarget
    st.metric(label="Productive Time Spending", value=f"{todayData["productivity"]} Min", delta=f"{productivityDelta:.0f} min (Target:{productivityTarget} min)")


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

def todayReviewExist(history):
    todayStr = date.today().isoformat()

    if not history:
        return None
    
    for review in history.get("ai_reviews", []):
        if review.get("date") == todayStr:
            return review
    return None

existingReview = todayReviewExist(fullHistory)

if existingReview:
    st.info("You have already generated today's report. Come back tomorrow.")

    scores = existingReview.get("scores", {})

    scCol1, scCol2, scCol3, scCol4 = st.columns(4)

    with scCol1:
        st.metric("Diet Score", f"{scores.get('diet', 0.0)}/10")
    with scCol2:
        st.metric("Water Score", f"{scores.get("water", 0.0)}/10")
    with scCol3:
        st.metric("Workout Score", f"{scores.get("workout", 0.0)}/10")
    with scCol4:
        st.metric("Productivity Score", f"{scores.get("productivity", 0.0)}/10")
                    
    st.divider()

    analysis = existingReview.get("analysis", {})
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
                "productivity": [],
                "ai_reviews": []
            }

            with open(USER_PROFILE_PATH, "r") as file:
                userProfileData = json.load(file)

            for category in ["diet", "water", "workout", "context", "productivity", "ai_reviews"]:
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
                        5. Weight and progress photos are only collected every 14 days as part of the fortnightly report , not daily. If "Current Weight" shows "Not Reported Today", this is completely normal and expected - do NOT comment on it or ask user to log it or treat it as missed task. Only reference weight/vision data on days its Available and present.

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
                                "workout": 0.0,
                                "productivity": 0.0
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
                    - Productivity: {todayData['productivity']}

                    PREVIOUS 14-DAY PERFORMANCE HISTORY:
                    {json.dumps(slicedHistory, indent=2)}

                    General User information: {userProfileData}
                    """

            with st.spinner("Analyzing your today's progress..."):
                try:
                    response = runAIdaily(SYSTEM_PROMPT, USER_PROMPT, imagePaths=todayImages)

                    if response:
                        st.success("AI Coach Analysis Complete!")

                        historicalData = {
                            "date": todayStr,
                            "scores": response.get("scores", {}),
                            "analysis": response.get("analysis", {})
                        }

                        saveData("ai_reviews", historicalData)

                        st.markdown("### Today's Performance Scores")
                        scores = response.get("scores", {})

                        scCol1, scCol2, scCol3, scCol4 = st.columns(4)

                        with scCol1:
                            st.metric("Diet Score", f"{scores.get('diet', 0.0)}/10")
                        with scCol2:
                            st.metric("Water Score", f"{scores.get("water", 0.0)}/10")
                        with scCol3:
                            st.metric("Workout Score", f"{scores.get("workout", 0.0)}/10")
                        with scCol4:
                            st.metric("Productivity Score", f"{scores.get("productivity", 0.0)}/10")
                    
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

st.divider()

st.markdown("### Weekly Recap")

def earliestLogDate(history):
    if not history:
        return None
    
    earliestDate = None
    categories = [
        "diet",
        "water",
        "workout",
        "context",
        "productivity"
    ]

    for category in categories:
        categoryRecords = history.get(category, [])
        for item in categoryRecords:
            itemDateStr = item.get("date", "")
            try:
                itemDate = datetime.date.fromisoformat(itemDateStr)
            except ValueError:
                continue

            if earliestDate is None:
                earliestDate = itemDate
            elif itemDate < earliestDate:
                earliestDate = itemDate
    return earliestDate

def weeklyRecapCheck(history):
    if not history:
        return False
    
    earliestDate = earliestLogDate(history)
    if earliestDate is None:
        return False
    
    todayDate = date.today()
    weeklyRecaps = history.get("weekly_recap", [])

    if not weeklyRecaps:
        daysSinceStart = (todayDate - earliestDate).days
        return daysSinceStart >= 7

    lastRecap = weeklyRecaps[-1]

    lastRecapDateStr = lastRecap.get("date")

    try:
        lastRecapDate = datetime.date.fromisoformat(lastRecapDateStr)
    except (ValueError, TypeError):
        return None
    
    daysSinceLastRecap = (todayDate - lastRecapDate).days

    return daysSinceLastRecap >= 7

if fullHistory:
    weeklyRecaps = fullHistory.get("weekly_recap", [])
else:
    weeklyRecaps = []

if weeklyRecaps:
    latestRecap = weeklyRecaps[-1]

    st.info(f"Latest Weekly Recap - {latestRecap.get('date')}")
    st.write(latestRecap.get("weekly_summary", ""))

    achievements = latestRecap.get("achievements", [])

    if achievements:
        st.markdown("#### Achievements")
        for item in achievements:
            st.write(item)

    areasToImprove = latestRecap.get("areas_to_improve", [])
    if areasToImprove:
        st.markdown("#### Areas to Improve")
        for item in areasToImprove:
            st.write(item)

    nextWeekFocus = latestRecap.get("next_week_focus", [])
    if nextWeekFocus:
        st.markdown("#### Next Week's Focus")
        for item in nextWeekFocus:
            st.info(item)
else:
    st.caption("No Weekly Recap Generated Yet :(")

if weeklyRecapCheck(fullHistory):
    btn = st.button("Generate Weekly Recap", type="primary")

    if btn:
        sevenDaysAgo = date.today() - datetime.timedelta(days=7)

        slicedWeek = {
            "diet": [],
            "water": [],
            "workout": [],
            "context": [],
            "productivity": []
        }

        for category in ["diet", "water", "workout", "context", "productivity"]:
            categoryRecords = fullHistory.get(category, [])
            
            for item in categoryRecords:
                itemDateStr = item.get("date", "")
                try:
                    itemDate = datetime.date.fromisoformat(itemDateStr)
                except ValueError:
                    continue

                if itemDate >= sevenDaysAgo and itemDate < date.today():
                    slicedWeek[category].append(item)
        
        SYSTEM_PROMPT_WEEKLY = """You are a health and fitness coach writing a weekly recap based on user's last 7 days of logs.
        
Your response MUST be a valid JSON object matching this exact structure, with no markdown code block backticks etc:
{
    "weekly_summary": "a short 2-3 sentence overview of how this week went overall",
    "achievements": ["list of specific things the user did well this week"],
    "areas_to_improve": ["list of specific, constructive areas needing attention"],
    "next_week_focus": ["1-3 specific, achievable goals for next week"]
}"""

        USER_PROMPT_WEEKLY = f"""
Here is the user's data for the past 7 days:
{json.dumps(slicedWeek, indent=2)}
"""
        
        with st.spinner("Compiling your weekly recap..."):
            try:
                weeklyResponse = runAIdaily(SYSTEM_PROMPT_WEEKLY, USER_PROMPT_WEEKLY)

                if weeklyResponse:
                    weeklyRecapData = {
                        "date": date.today().isoformat(),
                        "weekly_summary": weeklyResponse.get("weekly_summary", ""),
                        "achievements": weeklyResponse.get("achievements", []),
                        "areas_to_improve": weeklyResponse.get("areas_to_improve", []),
                        "next_week_focus": weeklyResponse.get("next_week_focus", [])
                    }

                    saveData("weekly_recap", weeklyRecapData)
                    st.success("Weekly Recap Generated!")
                    st.rerun()
                else:
                    st.error("Weekly Recap Generation failed :(")

            except Exception as e:
                st.error(f"Unexpected Error: {e}")
else:
    st.caption("Your next weekly recap will be available once the current week is over :)")