import json, re
from datetime import date, timedelta
from flask import Blueprint, request, jsonify
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

@coachChatBp.route("/coach-chat", methods = ["GET"])
def coachChat():
    recordData = loadFullRecordData()
    userProfile = loadUserProfile()

    if not recordData or not userProfile:
        return renderPage("Chat with Coach", "<p>Data Missing :(</p>")
    chatHistory = loadChatHistory()

    messagesHtml = ""

    if not chatHistory:
        messagesHtml += '<p class="caption">No Messages Yet - Say hi to your coach!</p>'
    else:
        for message in chatHistory:
            if message['role'] == "user":
                cls = "chat-user"
            else:
                cls = "chat-assistant"
            
            messagesHtml += f'<div class="chat-msg {cls}">{message["content"]}</div>'
    
    body = f"""
<h2>Chat with your AI Coach</h2>
<div class="card" id="chat-log">{messagesHtml}</div>
<div class="card">
    <textarea placeholder="Ask your coach anything..." id="chat-input"></textarea>
    <button id="send-btn" onclick="sendMessage()">Send</button>
</div>
<script>
    async function sendMessage() {{
        const input = document.getElementById("chat-input");
        const btn = document.getElementById("send-btn");
        const log = document.getElementById("chat-log");
        const message = input.value.trim();

        if (!message) return;

        log.querySelector(".caption")?.remove();

        log.innerHTML += `<div class="chat-msg chat-user">${{message}}</div>`;
        input.value = "";
        btn.disabled = true;
        btn.textContent = "Coach is thinking...";

        try {{
            const res = await fetch("/coach-chat/send", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{message}})
            }});

            const data = await res.json();

            if (data.error) {{
                log.innerHTML += `<div class="chat-msg chat-assistant">Error: ${{data.error}}</div>`;
            }}
            else {{
                log.innerHTML += `<div class="chat-msg chat-assistant">${{data.reply}}</div>`
            }}
        }} catch (e) {{
            log.innerHTML += `<div class="chat-msg chat-assistant">Error: Coach is Sleeping :(</div>`
        }}

        btn.disabled = false;
        btn.textContent = "Send";
        log.scrollTop = log.scrollHeight;
    }}
</script>
"""
    return renderPage("Chat with Coach", body)

def stripMd(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\*\-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", " ", text)

    return text.strip()

@coachChatBp.route("/coach-chat/send", methods = ["POST"])
def sendMessage():
    recordData = loadFullRecordData()
    userProfile = loadUserProfile()

    if not recordData or not userProfile:
        return jsonify({
            "error": "Data Missing"
        }), 400
    
    userMessage = (request.json or {}).get("message", "").strip()

    if not userMessage:
        return jsonify({
            "error": "Empty Message"
        }), 400
    
    historySummary = genContextSummary(recordData)
    chatHistory = loadChatHistory()

    SYSTEM_PROMPT = f"""
You are supportive and knowledgeable Health, fitness and productivity coach chatting directly with the user in conversational format and tone. You will be given access to user's profile, their last 14 days of logged data. Use the data to give personalized, specific and encouraging advice to user. Be hard, firm and strict on what's right - don't blindly agree with everything user says.

STRICT OUTPUT RULES - follow these exactly:
- Reply in 2 to 4 short sentences maximum, as one flowing paragraph.
- Never use bullet points, numbered lists, headers, bold, italics, asterisks, backticks, or any markdown syntax whatsoever.
- Do not respond in JSON.
- Write like a text message from a knowledgeable friend, not a report.

User Profile: {json.dumps(userProfile)}

Last 14 Days of Logged Data: {historySummary}
"""

    try:
        reply = runAIChat(SYSTEM_PROMPT, chatHistory, userMessage)
        reply = stripMd(reply)
        appendChatMessage("user", userMessage)
        appendChatMessage("assistant", reply)
        return jsonify({
            "reply": reply
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500