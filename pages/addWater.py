from flask import Blueprint, request, redirect
from datetime import datetime
from db import saveData
from layout import renderPage

addWaterBp = Blueprint("addWater", __name__)

@addWaterBp.route("/log/water", methods = [
    "GET",
    "POST"
])
def addWater():
    if request.method == "POST":
        now = datetime.now()
        data = {
            "date": request.form.get("date") or now.date().isoformat(),
            "time": request.form.get("time") or now.strftime("%H:%M:%S"),
            "amount": request.form.get("amount", "0")
        }

        saveData("water", data)
        return redirect("/")
    
    body = """
<h2>Log Water Intake</h2>
<form method="POST" class="card">
    <label>Date</label>
    <input type="date" name="date">
    <label>Time</label>
    <input type="time" name="time">
    <label>Amount (Litres)</label>
    <input type="number" name="amount" step="0.01" min="0.01">
    <button type="submit">Log Water Intake</button>
</form>
"""

    return renderPage("Log Water", body)