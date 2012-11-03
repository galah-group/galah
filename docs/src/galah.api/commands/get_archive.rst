get_archive
===========

Downloads all the submissions for a given assignment as a tarball. The tarball
is structures as follows:

.. code-block:: none

    user@school.edu
    |---- 2012-10-20-23-44-55
    |     |---- main.cpp
    |     +---- something_else.cpp
    |---- 2012-10-20-23-33-21
    +     +---- main.cpp
    other_user@schoole.edu
    |---- 2012-10-19-21-33-43
    +     +---- main.cpp

So the top level directories of the tarball will all be names of users, and
inside of each of the user directories there will be directories named by the
timestamp of the submission (following the format
``YEAR-MONTH-DAY-HOUR-MINUTE-SECOND``. Finally, inside of the timestamped
directories are the actual user submissions.

In the unlikely scenario that two submissions by the same user have the same
timestamp, the timestamped directory will follow the format
``YEAR-MONTH-DAY-HOUR-MINUTE-SECOND-RANDOMNUMBER``.

Reference
---------

.. function:: get_archie(assignment[, email = ""])
    
    :param assignment: The exact id of the assignment.
    :param email: You can optionally specify a user's email to filter on, and
                  only that user's submissions will be downloaded.

Example Usage
-------------

>>>  get_archive 5091654355c448096df90687
--Logged in as jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?: submissions-all.tar.gz
File saved to submissions-all.tar.gz.
>>> get_archive 5091654355c448096df90687 student@ucr.edu
--Logged in as jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?:  
File saved to ./submissions.tar.gz.