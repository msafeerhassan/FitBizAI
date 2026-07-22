import hmac, os
from flask import Blueprint, request, redirect, session
from layout import renderPage
from dotenv import load_dotenv

load_dotenv()

authBp = Blueprint("auth", __name__)

APP_PASSWORD = os.getenv("APP_PASSWORD")

@authBp.route("/login", methods=["GET", "POST"])

def login():
    error = None

    if request.method == "POST":
        submitted = request.form.get("password", "")

        if APP_PASSWORD and hmac.compare_digest(submitted, APP_PASSWORD):
            session["authenticated"] = True
            return redirect("/")

        error = "Incorrect Password :("

    if error:
        errorHtml = f'<p style="color: #dc2626;">{error}</p>'
    else:
        errorHtml = ""

    body = f"""
<h2>Login</h2>
{errorHtml}
<form method="POST" class="card">
    <label>Password</label>
    <input type="password" name="password" required>
    <button type="submit">Log In</button>
</form>
"""
    return renderPage("Login", body)

@authBp.route("/logout", methods = ["GET"])
def logout():
    session.clear()
    return redirect("/login")