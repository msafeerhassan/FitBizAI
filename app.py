from flask import Flask
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

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)