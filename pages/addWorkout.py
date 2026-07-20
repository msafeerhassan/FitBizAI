from flask import Blueprint, redirect, request
from datetime import datetime
from db import saveData
from layout import renderPage

addWorkoutBp = Blueprint("addWorkout", __name__)

@addWorkoutBp.route("/log/workout", methods = [
    "GET",
    "POST"
])

def addWorkout():
    if request.method == "POST":
        now = datetime.now()

        data = {
            "date": request.form.get("date") or now.date().isoformat(),
            "time": request.form.get("time") or now.strftime("%H:%M:%S"),
            "type": request.form.get("type", ""),
            "amount": request.form.get("amount", "1")
        }

        saveData("workout", data)

        return redirect("/")
    
    body = """
<h2>Log a Workout</h2>
<form method="POST" class="card">
    <label>Date</label>
    <input type="date" name="date">
    <label>Time</label>
    <input type="time" name="time">
    <label>Workout Type</label>
    <input type="text" name="type" placeholder="Pushups, Pullups etc.">
    <label>Number</label>
    <input type="number" name="amount" min="1">
    <button type="submit">Log Workout</button>
</form>
"""

    return renderPage("Log Workout", body)