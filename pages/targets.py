from flask import Blueprint, request, redirect
from db import loadUserProfile, saveUserProfile
from layout import renderPage

targetsBp = Blueprint("targets", __name__)

@targetsBp.route("/targets", methods = [
    "GET",
    "POST"
])

def targets():

    userProfile = loadUserProfile()

    if not userProfile:
        return renderPage("Targets", '<p>No user profile found - <a href="/signup">sign up first please</a></p>')

    waterTarget = userProfile.get("water_target_litres", 1.0)
    workoutTarget = userProfile.get("workout_sessions_target", 1)
    productivityTarget = userProfile.get("productivity_minutes_target", 10)

    if request.method == "POST":
        userProfile["water_target_litres"] = float(request.form.get("water", waterTarget))
        userProfile["workout_sessions_target"] = int(request.form.get("workout", workoutTarget))
        userProfile["productivity_minutes_target"] = int(request.form.get("productivity", productivityTarget))

        saveUserProfile(userProfile)
        return redirect("/targets")

    body = f"""
<h2>Goals & Targets</h2>
<form method="POST" class="card">
    <label>Water Target (Litres/day)</label>
    <input name="water" type="number" step="0.1" min="0.1" value="{waterTarget}">
    <label>Workout Sessions Target (per day)</label>
    <input name="workout" type="number" min="1" value="{workoutTarget}">
    <label>Productivity Target (minutes/day)</label>
    <input type="number" name="productivity" min="1" value="{productivityTarget}">
    <button type="submit">Save Targets</button>
</form>
"""
    
    return renderPage("Targets", body)