import json
from datetime import date, timedelta
from flask import Blueprint, request, redirect
from ai import runAIChat
from db import loadChatHistory, appendChatMessage, loadFullRecordData, loadUserProfile
from layout import renderPage

coachChatBp = Blueprint("coachChat", __name__)
    
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

    for category in slicedHistory:
        for item in data.get(category, []):
            itemDate = date.fromisoformat(item.get("date", ""))

            if forteenDaysAgo <=itemDate <= todayDate:
                slicedHistory[category].append(item)
    
    contextSummary = json.dumps(slicedHistory, indent=2)

    return contextSummary

@coachChatBp.route("/coach-chat", methods = ["GET", "POST"])
def coachChat():
    recordData = loadFullRecordData()
    userProfile = loadUserProfile()

    if not recordData or not userProfile:
        return renderPage("Chat with Coach", "<p>Data Missing :(</p>")
    
    if request.method == "POST":
        userMessage = request.form.get("message", "").strip()

        if userMessage:
            historySummary = genContextSummary(recordData)
            chatHistory = loadChatHistory()


            SYSTEM_PROMPT = f"""You are supportive and knowledgeable Health, fitness and productivity coach chatting directly with the user in conversational format and tone. You will be given access to user's profile, their last 14 days of logged data. Use the data to give personalized, specific and encouraging advice to user. Keep your responses conversational, concise and avoid sounding robotic in tone. Do not respond in JSON - just reply in plain, friendly text. Be hard, firm and strict on what's right - don't blindly agree with everything user says.


User Profile: {json.dumps(userProfile)}

Last 14 Days of Logged Data: {historySummary}
"""
            reply = runAIChat(SYSTEM_PROMPT, chatHistory, userMessage)

            appendChatMessage("user", userMessage)
            appendChatMessage("assistant", reply)
        return redirect("/coach-chat")

    chatHistory = loadChatHistory()

    body = '<h2>Chat with your AI Coach</h2><div class="card">'

    if not chatHistory:
        body += '<p class="caption">No Messages Yet - Say hi to your coach!</p>'
    else:
        for message in chatHistory:
            if message['role'] == "user":
                cls = "chat-user"
            else:
                cls = "chat-assistant"
            
            body += f'<div class="chat-msg {cls}">{message["content"]}</div>'
    
    body += "</div>"

    body += """
<form method="POST" class="card">
    <textarea name="message" placeholder="Ask your coach anything..." required></textarea>
    <button type="submit">Send</button>
</form>
"""

    return renderPage("Chat with Coach", body)