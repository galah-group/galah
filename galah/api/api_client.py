#!/usr/bin/env python

# The default configuration settings
config = {
    "galah_host": "http://localhost:5000",
}

import json
def _to_json(obj):
    """
    Serializes an object into a JSON representation. The returned string will be
    compressed appropriately for network transfer.
    
    """
    
    return json.dumps(obj, separators = (",", ":"))

def _form_call(api_name, *args, **kwargs):
    """
    Creates a tuple or dict (depending on the existence of keyword arguments)
    that can be serialized to JSON and sent to galah.api.
    
    """
    
    if not kwargs:
        return (api_name, ) + args
    else:
        # kwargs is basically already what we want, we just need to add the
        # positional arguments and name of the API call.
        kwargs.update({"api_name": api_name, "args": args})
        
        return kwargs

from warnings import warn
import requests

# We'll need to store any cookies the server gives us (mainly the auth cookie)
# and requests' sessions give us a nice way to do that.
session = requests.session()

def login(email, password):
    """
    Attempts to authenticate with Galah using the given credentials.

    """

    request = session.post(
        config["galah_host"] + "/api/login",
        data = {"email": email, "password": password}
    )
    
    request.raise_for_status()
    
    # Check if we successfully logged in.
    if request.headers["X-CallSuccess"] != "True":
        raise RuntimeError(request.text)
    
    # Nothing bad happened, go ahead and return what the server sent back
    return request.text

import time
def call(interactive, api_name, *args, **kwargs):
    """
    Makes an API call to the server with the given arguments. This function will
    block until the server sends its response.

    Iff interactive is True then call will take care of printing to the console
    itself, and will prompt the user if the server wants to push any downloads
    down, None is returned. Otherwise, pushes will be ignored and the text sent
    from the server will be returned, nothing will be printed to the console.
    
    """
    
    # May throw a requests.ConnectionError here if galah.api is unavailable.
    request = session.post(
        config["galah_host"] + "/api/call",
        data = _to_json(_form_call(api_name, *args, **kwargs)),
        headers = {"Content-Type": "application/json"}
    )
    
    # Will throw a requests.URLError or requests.HTTPError here if either
    # occurred.
    request.raise_for_status()
    
    # Currently only textual data is ever returned but other types of data may
    # be returned in the future. If this warning goes off that means that this
    # script needs to be updated to a new version.
    if not request.headers["Content-Type"].startswith("text/plain"):
        warn(
            "Expecting text/plain content, got %s. You may need to update this "
            "program." % request.headers["Content-Type"].split(";")[0]
        )
    
    # Check if the server encountered an error processing the request.
    # Unfortunately the status code can't be set to 500 on the server side
    # because of some issues with Flask, so we have this custom header.
    if request.headers["X-CallSuccess"] != "True":
        raise RuntimeError(request.text)

    # If we're not in interactive mode, our job is done already.
    if not interactive:
        return request.text

    print request.text

    # Check if the server wants us to download a file
    if "X-Download" in request.headers:
        default_name = request.headers.get(
            "X-Download-DefaultName", "downloaded_file"
        )

        print "The server is requesting that you download a file..."
        save_to = raw_input(
            "Where would you like to save it (default: ./%s)?: " % default_name
        )

        # If they don't type anything in, go with the default.
        if not save_to:
            save_to = "./" + default_name

        if os.path.isfile(save_to):
            confirmation = raw_input(
                "File %s already exists, would you like to overwrite it "
                "(y, n)? " % save_to
            )

            if not confirmation.startswith("y"):
                exit("Aborting.")

        # Actually grab the file from the server
        while True:
            file_request = session.get(
                config["galah_host"] + "/" + request.headers["X-Download"]
            )
            
            if file_request.status_code == requests.codes.ok:
                break

            print "Download not ready yet, waiting for server... Retrying " \
                  "in 2 seconds..."

            time.sleep(2)

        with open(save_to, "wb") as download_file:
            download_file.write(file_request.content)

        print "File saved to %s." % save_to
    
    # Nothing bad happened, go ahead and return what the server sent back
    return None

import sys
from optparse import OptionParser, make_option
def parse_arguments(args = sys.argv[1:]):
    option_list = [
        make_option(
            "--user", "-u", metavar = "USERNAME",
            help = "The username to authenticate with. The password should be "
                   "available in the evironmental variable GALAH_PASSWORD "
                   "if this option is used."
        ),
        make_option(
            "--config", "-c", metavar = "FILE",
            help = "The configuration file to use. By default "
                   "~/.galah/config/api_client.config is used if available."
        ),
        make_option(
            "--shell", "-s", action = "store_true",
            help = "If specified, you will be placed in an interactive "
                   "bash shell that will allow you to execute api commands as "
                   "if they were regular system commands."
        )
    ]

    parser = OptionParser(
        description = "Command line interface to Galah for use by instructors "
                      "and administrators.",
        option_list = option_list,
        epilog = "Example usage in bash: GALAH_PASSWORD=test python "
                 "api_client.py -u john@doe.com get_submissions "
                 "SOME0ASSIGNMENT0ID"
    )

    options, args = parser.parse_args(args)

    if not options.shell and len(args) == 0:
        parser.error("At least one argument must be supplied.")

    return (options, args)

def parse_configuration(config_file):
    import json

    config = json.load(config_file)

    return config

def exec_to_shell():
    # The name of the currently executing script (ex: api_client.py)
    script_location, script_name = os.path.split(__file__)
    script_location = os.path.abspath(script_location)

    # Retrieve all of the available commands from the server
    api_info = json.loads(call(False, "get_api_info"))
    commands = [i["name"] for i in api_info]

    rcfile_path = os.path.join(os.environ["HOME"], ".galah/tmp/shellrc")

    rcfile = None
    if "HOME" in os.environ:
        try:
            os.makedirs(os.path.dirname(rcfile_path))
        except OSError:
            pass

        try:
            rcfile = open(rcfile_path, "w")
        except IOError:
            pass

    if rcfile == None:
        rcfile, rcfile_path = tempfile.mkstemp()

        print rcfile_path
        sys.stdout.flush()

    # Add the location of the api client to the PATH
    print >> rcfile, "PATH=%s:$PATH" % script_location

    # Add the location of the man files to the MANPATH
    print >> rcfile, "export MANPATH=./man/:`manpath`"

    # Add aliases for each command that just wrap the api client
    for i in commands:
        print >> rcfile, 'alias %s="%s %s"' % (i, script_name, i)

    # Change the prompt a little bit so users know their in a modified shell
    print >> rcfile, 'PS1="\\[\033[1;34m\\](Galah) $PS1\\[\033[0m\\]"'

    # Manually ensure that there's nothing buffered as no cleanup will occur
    # when we exec below.
    rcfile.flush()

    os.execlp("bash", "bash", "--rcfile", rcfile_path)

import os
if __name__ == "__main__":
    options, args = parse_arguments()

    if options.shell:
        exec_to_shell()

    if options.config:
        try:
            config_file = open(options.config)

            config.update(parse_configuration(config_file))
        except IOError:
            exit("File '%s' could not be opened for reading." % config_file)
    else:
        try:
            config_file = open(os.path.join(
                os.environ["HOME"], ".galah/config/api_client.config"
            ))

            config.update(parse_configuration(config_file))
        except (IOError, KeyError):
            pass

    user = options.user or config.get("user")
    password = os.environ.get("GALAH_PASSWORD") or config.get("password")

    if user and not password:
        exit(
            "Username specified but no password given (did you forget to set "
            "GALAH_PASSWORD?)."
        )

    if user and password:
        try:
            login(user, password)

            print "--Logged in as %s--" % user
        except requests.exceptions.ConnectionError as e:
            print >> sys.stderr, "Could not connect with the given url '%s':" \
                    % config["galah_host"]
            print >> sys.stderr, "\t" + str(e)

            exit(1)
        except RuntimeError:
            print >> sys.stderr, "Could not log in with provided user name " \
                  "and password. (Did you remember to set GALAH_PASSWORD?)"

            exit(1)
    else:
        print "--Not logged in--"
    
    try:
        try:
            # This function actually outputs the result of the call to the
            # console.
            call(True, *args)
        except requests.exceptions.ConnectionError as e:
            print >> sys.stderr, "Could not connect with the given url '%s':" \
                    % config["galah_host"]
            print >> sys.stderr, "\t" + str(e)

            exit(1)

    except RuntimeError as e:
        print str(e)
