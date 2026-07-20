from flask import Blueprint, request, redirect
from datetime import datetime
from db import saveData
from layout import renderPage

addDietBp = Blueprint("addDiet", __name__)

@addDietBp.route("/log/diet", methods= [
    "POST",
    "GET"
])

def addDiet():
    if request.method == "POST":
        now = datetime.now()
        data = {
            "date": request.form.get("date") or now.date().isoformat(),
            "time": request.form.get("time") or now.strftime("%H:%M:%S"),
            "item": request.form.get("item", "")
        }

        saveData("diet", data)

        return redirect("/")
    
    body = """
<h2>Log a Meal</h2>
<form class="card" method="POST">
    <label>Date</label>
    <input type="date" name="date">
    <label>Time</label>
    <input type="time" name="time">
    <label>What did you cosume?</label>

    <textarea name="item" placeholder="20 Almonds, 5 Protein Bars..."></textarea>
    <button type="submit">Log Meal</button>
</form>
"""

    return renderPage("Log Meal", body)