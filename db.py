import os, requests

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get(path, params=None):
    response = requests.get(f"{SUPABASE_URL}/rest/v1/{path}", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def post(path, body, extra_headers=None):
    hd = dict(headers)

    if extra_headers:
        hd.update(extra_headers)
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers=hd,
        json=body
    )

    response.raise_for_status()

    if response.text:
        return response.json()
    else:
        return None

def patch(path, body):
    response = requests.patch(f"{SUPABASE_URL}/rest/v1/{path}", headers=headers, json=body)
    response.raise_for_status()
    
    if response.text:
        return response.json()
    else:
        return None

def delete(path):
    response = requests.delete(f"{SUPABASE_URL}/rest/v1/{path}", headers=headers)

    response.raise_for_status()

    if response.text:
        return response.json()
    else:
        return None
    
def saveData(category, data):
    if category == "ai_reviews":
        reserved = ("date",)
    else:
        reserved = ("date", "time")

    payload = {}

    for k, v in data.items():
        if k not in reserved:
            payload[k] = v
        
    body = {
        "category": category,
        "log_date": data.get("date"),
        "log_time": data.get("time", "00:00:00"),
        "payload": payload
    }

    post("logs", body)

def saveUserProfile(data):
    body = dict(data)
    body["id"] = 1
    post("profile", body, extra_headers={
        "Prefer": "resolution=merge-duplicates"
    })

def loadUserProfile():
    rows = get("profile", params={
        "id": "eq.1",
        "select": "*"
    })

    if rows:
        return rows[0]
    else:
        return None

def loadFullRecordData():
    rows = get("logs", params={
        "select": "id,category,log_date,log_time,payload",
        "order": "log_date.asc"
    })

    if not rows:
        return None
    
    data = {
        "diet": [],
        "water": [],
        "workout": [],
        "context": [],
        "productivity": [],
        "ai_reviews": [],
        "fortnightly": [],
        "weekly_recap": []
    }

    for row in rows:
        category = row["category"]
        payload = row["payload"] or {}

        if category == "ai_reviews":
            entry = {
                "date": row["log_date"],
                "_id": row["id"],
                **payload
            }
        else:
            entry = {
                **payload,
                "date": row["log_date"],
                "time": row["log_time"],
                "_id": row["id"]
            }
        
        data.setdefault(category, []).append(entry)

    return data

def updateLogEntry(entryId, updates):
    body = {}

    if "date" in updates:
        body["log_date"] = updates.pop("date")
    if "time" in updates:
        body["log_time"] = updates.pop("time")
    
    if updates:
        body["payload"] = updates
    
    patch(f"logs?id=eq.{entryId}", body)

def deleteLogEntry(entryId):
    delete(f"logs?id=eq.{entryId}")

def loadChatHistory():
    rows = get("chat_messages", params={
        "select": "role,content",
        "order": "created_at.asc"
    })

    return rows or []

def appendChatMessage(role, content):
    post("chat_messages", {
        "role": role,
        "content": content
    })

def uploadProgressPhoto(filename, fileBytes, contentType):
    url = f"{SUPABASE_URL}/storage/v1/object/progress-photos/{filename}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": contentType
    }

    response = requests.post(url, headers=headers, data=fileBytes)

    if not response.ok:
        raise Exception(f"Supabase Storage Upload Failed ({response.status_code}): {response.text}")

    return f"{SUPABASE_URL}/storage/v1/object/public/progress-photos/{filename}"