from flask import Flask
app = Flask("galah.web.galahweb")

app.config.update({
    "DEBUG": True,
    "SECRET_KEY": "Very Secure Key",
    "MONGODB": "galah",
    "SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "HOST_URL": "http://localhost:5000"
})

if not app.config.from_envvar("GALAH_WEB_CONFIG", silent = True) and \
        not app.config.from_pyfile("/etc/galah/web.config", silent = True):
    exit(
        "Environmental variable GALAH_WEB_CONFIG not set to valid file "
        "path and /etc/galah/web.config could not be loaded. Either point "
        "GALAH_WEB_CONFIG at a valid config file or place your config "
        "file at /etc/galah/web.config."
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
