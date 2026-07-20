from flask import Blueprint, request, redirect
from datetime import datetime
from db import saveData
from layout import renderPage

addContextBp = Blueprint("addContext", __name__)

@addContextBp.route("/log/context", methods = [
    "GET",
    "POST"
])

def addContext():
    if request.method == "POST":
        now = datetime.now()
        data = {
            "date": request.form.get("date") or now.date().isoformat(),
            "time": request.form.get("time") or now.strftime("%H:%M:%S"),
            "text": request.form.get("text", "")
        }
        saveData("context", data)
        return redirect("/")
    
    body = """
<h2>Log Additional Context</h2>
<form method="POST" class="card">
    <label>Date</label>
    <input type="date" name="date">
    <label>Time</label>
    <input type="time" name="time">
    <label>Context</label>
    <textarea name="text" placeholder="I missed workout because of a family emergency..."></textarea>
    <button type="submit">Log Additional Context</button>
</form>
"""

    return renderPage("Add Context", body)