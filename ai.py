from dotenv import load_dotenv
import os, json, requests

load_dotenv()

HCAI_KEY = os.getenv("HCAI_KEY")
BASE_URL = "https://ai.hackclub.com/proxy/v1"
model = "qwen/qwen3-32b"

def chat(messages, jsonMode=True):
    body = {
        "model": model,
        "stream": False,
        "messages": messages
    }

    if jsonMode:
        body["response_format"] = {
            "type": "json_object"
        }

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {HCAI_KEY}",
            "Content-Type": "application/json"
        },
        json=body,
        timeout=55
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

def runAIChat(SYSTEM_PROMPT, chatHistory, userMessage):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for msg in chatHistory:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    messages.append({
        "role": "user",
        "content": userMessage
    })

    return chat(messages, jsonMode=False)

def runAIdaily(SYSTEM_PROMPT, USER_PROMPT, imagePaths = None):
    userContent = [{
        "type": "text",
        "text": USER_PROMPT
    }]

    for url in (imagePaths or []):
        userContent.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": url
                }
            }
        )

    content = chat(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": userContent
            }
        ]
    )

    return json.loads(content)