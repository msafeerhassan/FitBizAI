import json, os

FILE_PATH = "record.json"
USER_PROFILE_PATH = "userProfile.json"
CHAT_HISTORY_PATH = "chatHistory.json"

def initDb():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        initialStructure = {
            "diet": [],
            "water": [],
            "workout": [],
            "context": [],
            "productivity": [],
            "fortnightly": [],
            "weekly_recap": []
        }

        with open(FILE_PATH, "w") as file:
            json.dump(initialStructure, file, indent=4)

def saveData(category, data):
    initDb()

    try:
        with open(FILE_PATH, "r") as file:
            currentData = json.load(file)
    except json.JSONDecodeError:
        currentData = {
            "diet": [],
            "water": [],
            "workout": [],
            "context": [],
            "productivity": [],
            "fortnightly": [],
            "weekly_recap": []
        }
    
    if category in currentData:
        currentData[category].append(data)
    else:
        currentData[category] = [data]

    with open(FILE_PATH, "w") as file:
        json.dump(currentData, file, indent=4, default=str)

def saveUserProfile(data):
    if not os.path.exists(USER_PROFILE_PATH) or os.stat(USER_PROFILE_PATH).st_size == 0:
        initialStructure = {
            "name": "",
            "age": 0,
            "height_in_cm": 0,
            "location": "",
            "water_target_litres": 1.0,
            "workout_sessions_target": 1,
            "productivity_minutes_target": 10
        }

        with open(USER_PROFILE_PATH, "w") as file:
            json.dump(initialStructure, file, indent=4)
    

    with open(USER_PROFILE_PATH, "w") as file:
        json.dump(data, file, indent=4, default=str)

def loadChatHistory():
    if not os.path.exists(CHAT_HISTORY_PATH) or os.stat(CHAT_HISTORY_PATH).st_size == 0:
        return []
    
    try:
        with open(CHAT_HISTORY_PATH, "r") as file:
            messages = json.load(file)
            return messages
    except json.JSONDecodeError:
        return []

def saveChatHistory(messages):
    with open(CHAT_HISTORY_PATH, "w") as file:
        json.dump(messages, file, indent=4, default=str)

def loadFullRecordData():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        return None
    
    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        return None

def saveFullRecordData(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4, default=str)

def loadUserProfile():
    if not os.path.exists(USER_PROFILE_PATH) or os.stat(USER_PROFILE_PATH).st_size == 0:
        return None

    try:
        with open(USER_PROFILE_PATH, "r") as file:
            profile = json.load(file)
            return profile
    except json.JSONDecodeError:
        return None