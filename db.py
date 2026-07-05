import json, os

FILE_PATH = "record.json"


def initDb():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        initialStructure = {
            "diet": [],
            "water": [],
            "workout": [],
            "context": [],
            "fortnightly": []
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
            "fortnightly": []
        }
    
    if category in currentData:
        currentData[category].append(data)
    else:
        currentData[category] = [data]

    with open(FILE_PATH, "w") as file:
        json.dump(currentData, file, indent=4, default=str)