from datetime import date
from flask import Blueprint, request, redirect
from db import loadFullRecordData, updateLogEntry, deleteLogEntry
from layout import renderPage

manageLogsBp = Blueprint("manageLogs", __name__)

categoryFields = {
    "diet": [("item", "text")],
    "water": [("amount", "number")],
    "workout": [("type", "text"), ("amount", "number")],
    "context": [("text", "text")],
    "productivity": [("type", "text"), ("time_spent", "number")]
}

def getEarliestDate(data):
    earliest = None

    for category in categoryFields:
        for item in data.get(category, []):
            itemDate = date.fromisoformat(item.get("date", ""))

            if earliest is None or itemDate < earliest:
                earliest = itemDate
    
    return earliest

def getDateAndTime(item):
    dateX = item.get("date", "")
    time = item.get("time", "")

    return f"{dateX} {time}"

def sortEntries(records, startDate, endDate):
    filtered = []

    for entry in records:
        entryDate = date.fromisoformat(entry.get("date", ""))

        if startDate <= entryDate <= endDate:
            filtered.append(entry)
        
    filtered.sort(key=getDateAndTime, reverse=True)

    return filtered

def renderEntryLine(category, entry, startStr, endStr):
    entryId = entry.get("_id")

    if category == "diet":
        label = f"{entry.get("date")} {entry.get("time")} - {entry.get("item")}"
    elif category == "water":
        label = f"{entry.get("date")} {entry.get("time")} - {entry.get("amount")} L"
    elif category == "workout":
        label = f"{entry.get("date")} {entry.get("time")} - {entry.get("type")} ({entry.get("amount")})"
    elif category == "context":
        label = f"{entry.get("date")} {entry.get("time")} - {entry.get("text")}"
    else:
        label = f"{entry.get("date")} {entry.get("time")} - {entry.get("type")} ({entry.get("time_spent")} minutes)"
    
    return f"""
<div class="card" style="display: flex; justify-content: space-between; align-items: center;">
    <span>{label}</span>
    <span>
        <a href="/manage-logs/edit/{entryId}?category={category}&start={startStr}&end={endStr}">Edit</a>
        &nbsp;
        <form action="/manage-logs/delete/{entryId}" method="POST" style="display: inline;">
            <input type="hidden" name="category" value="{category}">
            <input type="hidden" name="start" value="{startStr}">
            <input type="hidden" name="end" value="{endStr}">
            <button type="submit" onclick="return confirm('Delete this entry?')">Delete</button>
        </form>
    </span>
</div>
"""

@manageLogsBp.route("/manage-logs", methods = ["GET"])
def manageLogs():
    recordData = loadFullRecordData()

    if not recordData:
        return renderPage("Manage Logs", "<p>No Data Recorded Yet - Nothing to Manage Here :(</p>")
    
    earliestDate = getEarliestDate(recordData) or date.today()
    todayStr = date.today().isoformat()

    startStr = request.args.get("start") or earliestDate.isoformat()
    endStr = request.args.get("end") or todayStr

    startDate = date.fromisoformat(startStr)
    endDate = date.fromisoformat(endStr)

    body = f"""
<h2>Manage Logs</h2>
<form class="card" method="GET">
    <label>From</label>
    <input type="date" name="start" value="{startStr}">
    <label>To</label>
    <input type="date" name="end" value="{endStr}">
    <button type="submit">Filter</button>
</form>    
"""
    
    labels = {
        "diet": "Diet",
        "water": "Water",
        "workout": "Workout",
        "context": "Context",
        "productivity": "Productivity"
    }

    for category, label in labels.items():
        body += f"<h3>{label}</h3>"

        entries = sortEntries(recordData.get(category, []), startDate ,endDate)

        if not entries:
            body += f'<p>No {label.lower()} entries in this date range</p>'
        else:
            for entry in entries:
                body += renderEntryLine(category, entry, startStr, endStr)
    return renderPage("Manage Logs", body)

@manageLogsBp.route("/manage-logs/edit/<entryId>", methods = [
    "GET",
    "POST"
])
def editLog(entryId):
    if request.method == "GET":
        category = request.args.get("category")
    else:
        category = request.form.get("category")
    if request.method == "GET":
        startStr = request.args.get("start")
    else:
        startStr = request.form.get("start", "")
    if request.method == "GET":
        endStr = request.args.get("end")
    else:
        endStr = request.form.get("end", "")

    if category not in categoryFields:
        return redirect("/manage-logs")
    
    if request.method == "POST":
        updates = {
            "date": request.form.get("date"),
            "time": request.form.get("time")
        }

        for fieldName, _ in categoryFields[category]:
            updates[fieldName] = request.form.get(fieldName)
        
        updateLogEntry(entryId, updates)

        return redirect(f"/manage-logs?start={startStr}&end={endStr}")
    
    recordData = loadFullRecordData() or {}

    entry = None

    categoryItems = recordData.get(category, [])

    for e in categoryItems:
        if str(e.get("_id")) == entryId:
            entry = e
            break
    
    if not entry:
        return renderPage("Edit Entry", "<p>Entry not found :(</p>")
    
    fieldsHtml = ""

    for fieldName, fieldType in categoryFields[category]:
        if fieldType == "text" and fieldName in ("item", "text"):
            fieldsHtml += f'<label>{fieldName.title()}</label><textarea name="{fieldName}">{entry.get(fieldName, "")}</textarea>'
        else:
            if fieldType == "number":
                inputType = "number"
            else:
                inputType = "text"
            
            fieldsHtml += f'<label>{fieldName.replace("_", " ").title()}</label><input type="{inputType}" name="{fieldName}" value="{entry.get(fieldName, "")}">'
    
    body = f"""
    <h2>Edit {category.title()} Entry</h2>
<form method="POST" class="card">
    <input type="hidden" name="category" value="{category}">
    <input type="hidden" name="start" value="{startStr}">
    <input type="hidden" name="end" value="{endStr}">
    <label>Date</label>
    <input type="date" name="date" value="{entry.get('date', '')}">
    <label>Time</label>
    <input type="time" name="time" value="{entry.get('time', '')}">
    {fieldsHtml}
    <button type="submit">Save Changes</button>
</form>
"""
    return renderPage("Edit Entry", body)

@manageLogsBp.route("/manage-logs/delete/<entryId>", methods = ["POST"])
def deleteLog(entryId):
    startStr = request.form.get("start", "")
    endStr = request.form.get("end", "")
    deleteLogEntry(entryId)

    return redirect(f"/manage-logs?start={startStr}&end={endStr}")