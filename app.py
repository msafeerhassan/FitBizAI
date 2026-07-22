from datetime import date
from flask import Flask, redirect, request, session
from home import homeBp
from insights import insightsBp
from signup import signupBp
from pages.targets import targetsBp
from pages.addDiet import addDietBp
from pages.addWater import addWaterBp
from pages.addWorkout import addWorkoutBp
from pages.addProductivity import addProductivityBp
from pages.addContext import addContextBp
from pages.fortnightlyLog import fortnightlyBp
from pages.progressPhotos import progressPhotosBp
from pages.achievements import achievementsBp
from pages.manageLogs import manageLogsBp
from pages.coachChat import coachChatBp
from auth import authBp
from db import loadUserProfile, loadFullRecordData
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(authBp)
app.register_blueprint(homeBp)
app.register_blueprint(insightsBp)
app.register_blueprint(signupBp)
app.register_blueprint(targetsBp)
app.register_blueprint(addDietBp)
app.register_blueprint(addWaterBp)
app.register_blueprint(addWorkoutBp)
app.register_blueprint(addProductivityBp)
app.register_blueprint(addContextBp)
app.register_blueprint(fortnightlyBp)
app.register_blueprint(progressPhotosBp)
app.register_blueprint(achievementsBp)
app.register_blueprint(manageLogsBp)
app.register_blueprint(coachChatBp)

def fortnightCheck():
    history = loadFullRecordData()

    if not history:
        return True
    
    fortnightlyLogs = history.get("fortnightly", [])

    if not fortnightlyLogs:
        return True
    
    try:
        lastLogDate = date.fromisoformat(fortnightlyLogs[-1].get("date"))
    except (ValueError, TypeError):
        return True
    
    return (date.today() - lastLogDate).days >= 14

exemptPaths = ("/signup", "/fortnightly")

@app.before_request
def gatekeeper():

    if request.path == "/login":
        return None

    if not session.get("authenticated"):
        return redirect("/login")

    profile = loadUserProfile()

    if request.path == "/signup":
        if profile:
            return redirect("/")
        return None
    if not profile:
        return redirect("/signup")
    
    if request.path == "/fortnightly":
        if not fortnightCheck():
            return redirect("/")
        return None
      
    if fortnightCheck():
        return redirect("/fortnightly")
    
    return None

if __name__ == "__main__":
    app.run(debug=True)