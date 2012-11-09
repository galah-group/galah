from flask import Response, request
from galah.web.galahweb import app, oauth_enabled
from flask.ext.login import current_user
from galah.api.commands import api_calls
from galah.db.crypto.passcrypt import check_seal, deserialize_seal
from galah.db.models import User
from flask.ext.login import login_user
from galah.web.galahweb.auth import FlaskUser

def get_many(dictionary, *args):
    return dict((i, dictionary.get(i)) for i in args)

@app.route("/api/login", methods = ["POST"])
def api_login():
    password = request.form.get("password", None)
    email = request.form["email"]

    # Optional arguments for OAuth2 Login
    access_token = request.form.get("access_token", None)
    audience = app.config["GOOGLE_CLIENT_ID"] if oauth_enabled else None
    def verify_token(email, audience, access_token):
        """
        Sends a request to the Google tokeninfo backend to verify access_token

        """
        import requests
        req = requests.post(
            "https://www.googleapis.com/oauth2/v1/tokeninfo",
            data={"access_token":access_token}
        )

        req.raise_for_status()

        if req.status_code == 400:
            raise RuntimeError(req.text)

        # Access token looks fine, now verify user's email matches.
        if req.json["email"] != email:
            raise RuntimeError("Attempting to login as different user")

        # Validate client id is matching to avoid confused deputy attack
        if req.json["audience"] != audience:
            raise RuntimeError("Invalid Client ID or OAuth2 not enabled")

        # Looks like the key is valid
        return True

    # Pull the user object with the given email from the database if it exists.
    try:
        user = FlaskUser(User.objects.get(email = email))
    except User.DoesNotExist:
        user = None
    
    # Check if the entered password is correct or, if no password, that the
    # access token can be validated using the Google tokeninfo backend.
    if not user or \
       not(password) and not(verify_token(email, audience, access_token)) and \
       not check_seal(password, deserialize_seal(str(user.seal))):
        return Response(
            response = "Incorrect email or password.",
            headers = {"X-CallSuccess": "False"}
        )
    else:
        login_user(user)
        
        return Response(
            response = "Successfully logged in.",
            headers = {"X-CallSuccess": "True"}
        )

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
