# Default configuration values for Galah.
defaults = {
    "global/SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "global/MONGODB": "galah",
    "global/HEAVYLIFTER_ADDRESS": "ipc:///tmp/heavylifter.sock",
    "web/DEBUG": True,
    "web/SECRET_KEY": "Very Secure Key",
    "web/HOST_URL": "http://localhost:5000"
}

import imp
import logging
from galah.base.utility import tuplify
from galah.base.magic import memoize

loaded = None
@memoize
def load_config(domain):
    """
    Parses and loads up the Galah configuration file and extracts the
    configuration data for the given domain (ex: "web" or "sheep").

    Global configuration options will always be returned, no matter the domain.

    The configuration file will only be loaded once per instance of the
    interpreter, so feel free to call this function multiple times in many files
    to avoid ugly dependency issues.

    """

    global loaded

    # Note whether this is the first time we're processing the configuraiton. If
    # it is, we'll want to attach the global log handlers.
    first_load = loaded is None

    # Load the configuration if it hasn't been loaded yet. Note this ensures
    # that the configuration is only loaded once per instance of the
    # interpreter
    if not loaded:
        try:
            loaded = imp.load_source(
                "user_config_file", "/etc/galah/galah.config"
            )
        except IOError:
            pass

    local_config = {}

    # Note we make a **shallow** copy of the defaults here
    user_config = dict(defaults)

    # If the configuration didn't load correctly, just use the defaults
    if loaded:
        user_config.update(loaded.config)

    # The prefix values we will look for when scanning the configuration file.
    prefix = "%s/" % domain
    global_prefix = "global/"

    # Grab all the configuration values for the given domain, and any global
    # configuration values.
    for k, v in user_config.items():
        if k.startswith(prefix) and k != len(prefix):
            local_key = k[len(prefix):]

            local_config[local_key] = v

            # If the user specified domain specific handlers, attach them to the
            # coorect logger. We know this will never be done multiple times
            # because this function is memoized.
            if local_key == "LOG_HANDLERS":
                handlers = tuplify(v)

                for i in handlers:
                    logging.getLogger("galah." + domain).addHandler(i)
        elif k.startswith(global_prefix) and k != len(global_prefix):
            global_key = k[len(global_prefix):]

            local_config[global_key] = v

            # If the user specified global log handlers, attach them to the
            # root logger.
            if first_load and global_key == "LOG_HANDLERS":
                handlers = tuplify(v)

                for i in handlers:
                    logging.getLogger("galah").addHandler(i)

    return local_config
