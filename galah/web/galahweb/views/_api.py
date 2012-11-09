from flask import Response, request
from galah.web.galahweb import app, oauth_enabled
from flask.ext.login import current_user
from galah.api.commands import api_calls
from galah.db.crypto.passcrypt import check_seal, deserialize_seal
from galah.db.models import User
from flask.ext.login import login_user
from galah.web.galahweb.auth import FlaskUser
import requests

def get_many(dictionary, *args):
    return dict((i, dictionary.get(i)) for i in args)

@app.route("/api/login", methods = ["POST"])
def api_login():
    password = request.form.get("password", None)
    email = request.form.get("email", None)

    def success(the_user):
        login_user(the_user)
        
        return Response(
            response = "Successfully logged in.",
            headers = {"X-CallSuccess": "True"}
        )

    def failure():
        return Response(
            response = "Incorrect email or password.",
            headers = {"X-CallSuccess": "False"}
        )

    # If the user is trying to login by giving us an access_token they got from
    # signing in through google, validate the token.
    access_token = request.form.get("access_token", None)
    if access_token and oauth_enabled:
        # Ask google to verify that they authed the user.
        req = requests.post(
            "https://www.googleapis.com/oauth2/v1/tokeninfo",
            data = { "access_token": access_token }
        )

        if req.status_code != requests.codes.ok:
            return failure()

        # Validate client id is matching to avoid confused deputy attack
        if req.json["audience"] != app.config["GOOGLE_APICLIENT_ID"]:
            raise RuntimeError("Invalid Client ID")

        # Grab the user from the database (here we also check to make sure that
        # this user actually has account on Galah).
        try:
            user = FlaskUser(User.objects.get(email = req.json["email"]))
        except User.DoesNotExist:
            return failure()

        return success(user)
    elif access_token and not oauth_enabled:
        raise RuntimeError("Login via OAuth2 is not configured.")
    
    # If the user is trying to authenticate through Galah...
    if email and password:
        try:
            user = FlaskUser(User.objects.get(email = email))
        except User.DoesNotExist:
            return failure()

        if check_seal(password, deserialize_seal(str(user.seal))):
            return success(user)
        else:
            return failure()
    
    raise RuntimeError("Malformed Request")

@app.route("/api/call", methods = ["POST"])
def api_call():
    try:
        # Make sure we got some data we can work with
        if request.json is None:
            raise RuntimeError("No request data sent.")

        # The top level object must be either a non-empty list or a dictionary
        # with an api_call key. They will have similar information either way
        # however, so here we extract that information.
        if type(request.json) is list and request.json:
            # The API call's name is the first item in the list, so use that
            # to grab the actual APICall object we need.
            api_name = request.json.pop(0)

            api_args = list(request.json)

            api_kwargs = {}
        elif type(request.json) is dict and "api_name" in request.json:
            # Don't let the user insert their own current_user argument
            if "current_user" in request.json:
                raise ValueError("You cannot fool the all-knowing Galah.")
                
            # Resolve the name of the API call and retrieve the actual
            # APICall object we need.
            api_name = request.json["api_name"]
            api_args = request.json["args"]

            del request.json["api_name"]
            del request.json["args"]

            api_kwargs = dict(**request.json)
        else:
            raise ValueError("Request data not formed correctly.")

        if api_name in api_calls:
            api_call = api_calls[api_name]
        else:
            raise RuntimeError("%s is not a recognized API call." % api_name)

        call_result = api_call(current_user, *api_args, **api_kwargs)

        # If an API call returns a tuple, the second item will be headers that
        # should be added onto the response.
        response_headers = {"X-CallSuccess": True}
        if isinstance(call_result, tuple):
            response_text = call_result[0]
            response_headers.update(call_result[1])
        else:
            response_text = call_result

        print "Headers:", response_headers

        return Response(
            response = response_text,
            headers = response_headers,
            mimetype = "text/plain"
        )
    except Exception as e:
        app.logger.exception("Exception occured while processing API request.")
        
        return Response(
            response = "An error occurred processing your request: %s" % str(e),
            headers = {"X-CallSuccess": "False"},
            mimetype = "text/plain"
        )
