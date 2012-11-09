Galah API
=========

Summary
-------

This is a complete reference to Galah's outward facing API.

Using the API
-------------

To execute the commands listed below in the :ref:`command_reference`, you must
use the api_client.py client. It works by packaging up any commands you want to
execute into HTTP requests, and sending them to the Galah web server.

Configuring the API Client
^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you use api_client.py you need to configure it so that it knows where the
Galah web server is, and so that it knows your credentials so it can log in as
you.

There are a variety of locations the API client will look in for your
configuration file. They are listed, in order, below:

.. code-block:: bash

	~/.galah/config/api_client.config
	/etc/galah/api_client.config
	./api_client.config

Further, if you set the ``GALAH_CONFIG_PATH`` environmental variable to be a
colon delimitted list of values (just like the ``PATH`` variable), those paths
will be searched in order first.

To debug issues with the API Client finding your configuration file, you can
run the API client with the ``--config-path`` flag to have it list all the
locations it checks for configuration files.

Once you decide where to put this configuration file, you need to populate it
with values. Below is an example of a configuration file (all configuration
options are listed in this example):

.. code-block:: js

	{
		"galah_host": "http://www.galahserver.com",
		"galah_home": "~/.galah",
		"user": "myemail@school.edu",
		"password": "plaintext password",
		"use_oauth": false
	}

**Make sure to set the permissions of your api_client.config file to 600 so
other users can't access it.**

If you are uncomfortable storing your password as plain text, you can safely
leave it out of the configuration and you will be prompted when logging in.
Altenatively, set the environmental variable **GALAH_PASSWORD** before running
the API client, and that password will be used.

If you set ``use_oauth`` to true, when you have to login, a web browser will be
opened and you will be authenticated with google. You do not have to specify
a password to the API client in this case, but make sure to set your user to
the user you will log into google with.

Also make sure to replace ``www.galahserver.com`` with the address of your
institution's Galah web server. You may also want to use *https* vs *http*
depending on your institution's installation.

``galah_home`` is where the ``tmp/`` directory will be stored, and other
directories and files may find there way in there as well.

Examples Using the API Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to use the API client is to execute the api_client.py file
with the command and the arguments you want to pass to it.

>>> api_client.py find_user jsull
--Logged in as jsull003@ucr.edu--
1 user(s) found matching query {email contains 'jsull'}.
	User [email = jsull003@ucr.edu, account_type = admin]

It can be bothersome to continually type out api_client.py over and over again
if you are executing multiple commands however. Therefore **you can enter a
shell** by running the command ``api_client.py -s`` which will place you into an
interactive shell. Within this shell, you can simply enter the commands followed
by their arguments (you can even use tab completion for the commands).

All examples in the :ref:`command_reference` below assume you're in the
interactive shell.

If you downloaded the official API client tarball (download link not yet
available, run the generate_apiclient_tarbell.sh command to create it) you will
be able to access man pages on every command by typing ``man`` and then the
command (ex: ``man find_user``). The man pages are just copies of the below
documentation files.

.. _command_reference:

Command Reference
-----------------

Below is reference material for every API command Galah supports.

.. toctree::
	:maxdepth: 1

	commands/create_user

	commands/find_user

	commands/user_info

	commands/delete_user

	commands/modify_user

	commands/reset_password

	commands/find_class

	commands/enroll_student

	commands/drop_student

	commands/create_class

	commands/delete_class

	commands/class_info

	commands/modify_class

	commands/create_assignment

	commands/modify_assignment

	commands/delete_assignment

	commands/assignment_info

	commands/get_archive