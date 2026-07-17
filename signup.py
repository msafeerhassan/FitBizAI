from flask import Blueprint, request, redirect
from layout import renderPage
from db import saveUserProfile

signupBp = Blueprint("signup", __name__)

@signupBp.route("/signup", methods = [
    "GET",
    "POST"
])

def signup():
    if request.method == "POST":
        data = {
            "name": request.form.get("name", ""),
            "age": int(request.form.get("age", 13)),
            "height_in_cm": int(request.form.get("height", 50)),
            "location": request.form.get("location", "")
        }

        saveUserProfile(data)
        return redirect("/")
    
    body = """
<h2>Sign Up</h2>
<form method="POST" class="card">
    <label>Name</label>
    <input name="name" required>
    <label>Age</label>
    <input type="number" name="age" min="13" required>
    <label>Height (cm)</label>
    <input type="number" name="height" min="50" required>
    <label>Location</label>
    <input name="location" placeholder="Texas, US" required>
    <button type="submit">Sign Up</button>
</form>
    """

    return renderPage("Sign Up", body)