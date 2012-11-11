from flask import Flask
app = Flask("galah.web")

app.config.update({
    "DEBUG": True,
    "SECRET_KEY": "Very Secure Key",
    "MONGODB": "galah",
    "SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "HOST_URL": "http://localhost:5000"
})

from galah.base.config import load_config
try:
    app.config.update(load_config("/etc/galah/galah.codnfig", "web"))
except IOError as e:
    exit(
        "Could not load config file at /etc/galah/web.config.\n\t" + str(e)
    )

if "LOG_HANDLERS" in app.config:
    import logging
    
    # If a single handler was passed directly, convert it into a one-tuple
    if isinstance(app.config["LOG_HANDLERS"], logging.Handler):
        app.config["LOG_HANDLERS"] = (app.config["LOG_HANDLERS"], )
        
    # Add any handlers the user wants
    for i in app.config["LOG_HANDLERS"]:
        app.logger.addHandler(i)

oauth_enabled = bool(
    app.config.get("GOOGLE_SERVERSIDE_ID") and
    app.config.get("GOOGLE_SERVERSIDE_SECRET") and
    app.config.get("GOOGLE_APICLIENT_ID") and
    app.config.get("GOOGLE_APICLIENT_SECRET")
)

import mongoengine
mongoengine.connect(app.config["MONGODB"])

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

import views
