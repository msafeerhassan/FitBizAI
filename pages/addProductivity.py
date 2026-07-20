from flask import Blueprint, request, redirect
from datetime import datetime
from db import saveData
from layout import renderPage

addProductivityBp = Blueprint("addProductivity", __name__)

@addProductivityBp.route("/log/productivity", methods = [
    "GET",
    "POST"
])

def addProductivity():
    if request.method == "POST":
        now = datetime.now()
        data = {
            "date": request.form.get("date") or now.date().isoformat(),
            "time": request.form.get("time") or now.strftime("%H:%M:%S"),
            "type": request.form.get("type", ""),
            "time_spent": request.form.get("time_spent", "1")
        }

        saveData("productivity", data)

        return redirect("/")
    
    body = """
<h2>Log Work / Productive Time</h2>
<form method="POST" class="card">
    <label>Date</label>
    <input type="date" name="date">
    <label>Time</label>
    <input type="time" name="time">
    <label>Work Type</label>
    <input type="text" name="type" placeholder="Coding, Studying etc.">
    <label>Minutes Spent</label>
    <input type="number" name="time_spent" min="1">
    <button type="submit">Log Work</button>
</form>
"""

    return renderPage("Log Work", body)

