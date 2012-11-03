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


You do this by creating a json file at **~/.galah/config/api_client.config**
with the following format::

	{
		"api_url": "http://www.galahserver.com/api/call",
		"login_url": "http://www.galahserver.com/api/login",
		"user": "myemail@school.edu",
		"password": "plaintext_password"
	}

**Make sure to set the permissions of your api_client.config file to 600 so
other users can't access it.**

If you are uncomfortable storing your password as plain text, you can set the
environmental variable **GALAH_PASSWORD** before running the API client, and
that password will be used (in this case you can just leave out the password
field in the api_client.config file entirely).

Also make sure to replace **www.galahserver.com** with the address of your
institution's Galah web server. You may also want to use *https* vs *http*
depending on your institution's installation.

Examples Using the API Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to use the API client is to execute the api_client.py file
with the command and the arguments you want to pass to it.

>>> api_client.py find_user jsull
--Logged in as jsull003@ucr.edu--
1 user(s) found matching query {email contains 'jsull'}.
	User [email = jsull003@ucr.edu, account_type = admin]

It can be bothersome to continually type out api_client.py over and over again
if you are executing multiple commands however. Therefore you can enter a shell
by running the command ``api_client.py -s`` which will place you into an
interactive shell. Within this shell, you can simply enter the commands followed
by their arguments (you can even use tab completion for the commands).

All examples in the :ref:`command_reference` below assume you're in the
interactive shell.

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