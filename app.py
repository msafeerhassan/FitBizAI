from flask import Flask
from home import homeBp
from insights import insightsBp
from signup import signupBp
from pages.targets import targetsBp

app = Flask(__name__)

app.register_blueprint(homeBp)
app.register_blueprint(insightsBp)
app.register_blueprint(signupBp)
app.register_blueprint(targetsBp)

if __name__ == "__main__":
    app.run(debug=True)