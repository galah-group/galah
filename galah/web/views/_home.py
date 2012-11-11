from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import redirect, url_for, flash

@app.route("/home")
@app.route("/", methods = ["GET", "POST"])
def home():
    if not current_user.is_authenticated():
        return redirect(url_for("login"))
    
    return redirect(url_for("browse_assignments"))
