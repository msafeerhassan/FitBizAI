import streamlit as st
import json, os
from datetime import date, timedelta
from db import loadChatHistory, saveChatHistory
from ai import runAIChat

st.header("Chat with your AI Coach")

FILE_PATH = "record.json"
USER_PROFILE_PATH = "userProfile.json"

def loadRecordData():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        return None
    
    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)

            return data
        
    except json.JSONDecodeError:
        return None
    
def loadUserProfile():
    if not os.path.exists(USER_PROFILE_PATH) or os.stat(USER_PROFILE_PATH).st_size == 0:
        return None
    
    try:
        with open(USER_PROFILE_PATH, "r") as file:
            profile = json.load(file)
            return profile
    except json.JSONDecodeError:
        return None
    
def genContextSummary(data):
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

    categories = ["diet", "water", "workout", "context", "productivity", "ai_reviews"]

    for category in categories:
        categoryRecords = data.get(category, [])

        for item in categoryRecords:
            itemDateStr = item.get("date", "")

            try:
                itemData = date.fromisoformat(itemDateStr)
            except ValueError:
                continue

            if itemData >= forteenDaysAgo and itemData <= todayDate:
                slicedHistory[category].append(item)
    
    contextSummary = json.dumps(slicedHistory, indent=2)

    return contextSummary

recordData = loadRecordData()
userProfile = loadUserProfile()

if not recordData or not userProfile:
    st.info("Data Missing :(")
    st.stop()

historySummary = genContextSummary(recordData)

SYSTEM_PROMPT = f"""You are supportive and knowledgeable Health, fitness and productivity coach chatting directly with the user in conversational format and tone. You will be given access to user's profile, their last 14 days of logged data. Use the data to give personalized, specific and encouraging advice to user. Keep your responses conversational, concise and avoid sounding robotic in tone. Do not respond in JSON - just reply in plain, friendly text. Be hard, firm and strict on what's write - don't blindly agree with everything user says.


User Profile: {json.dumps(userProfile)}

Last 14 Days of Logged Data: {historySummary}
"""

chatHistory = loadChatHistory()

for message in chatHistory:
    with st.chat_message(message["role"]):
        st.write(message["content"])

userMessage = st.chat_input("Ask your coach anything...")

if userMessage:
    with st.chat_message("user"):
        st.write(userMessage)

    with st.chat_message("assistant"):
        with st.spinner("Coach is thinking..."):
            reply = runAIChat(SYSTEM_PROMPT, chatHistory, userMessage)
            st.write(reply)
    
    chatHistory.append({
        "role": "user",
        "content": userMessage
    })

    chatHistory.append({
        "role": "assistant",
        "content": reply
    })

    saveChatHistory(chatHistory)