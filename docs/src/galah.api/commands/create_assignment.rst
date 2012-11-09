create_assignment
=================

Creates an assignment.

Reference
---------

.. function:: create_assignment(name, due, for_class[, due_cutoff = '', hide_until = '']):
    
    :param name: The name of the assignment.

    :param due: The due date of the assignmet, ex: "10/20/2012 10:09:00".

    :param for_class: The class the assignment is fors.

    :param due_cutoff: The cutoff date of the assignment (same format as due).
                       After the cutoff date, students won't even be able to
                       submit at all.

	:param hide_until: If specified, the assignment will not be visible to users
                       until this time. If ``none`` is specified, the previous
                       hide-until date is removed.

    :raises RuntimeError: If you are not a teacher of for_class and not an
    					  admin.

Example Usage
-------------

Here we will create an assignment named **World Domination** due on
**October 31, 2012 at 10:09 AM** for the class **CS 9000**.

>>> create_assignment "World Domination" "10/31/2012 10:09:00" CS\ 9000
--Logged in as jsull003@ucr.edu--
Success! Assignment [id = 50907cca55c4481a5027103c, name = World Domination] created.

If we want students to not be able to submit at all after midnight of October
31, we could instead do this.

>>> create_assignment "World Domination" "10/31/2012 10:09:00" CS\ 9000 "10/31/2012 23:59:00"
--Logged in as jsull003@ucr.edu--
Success! Assignment [id = 50907db055c4481a5027103d, name = World Domination] created.

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
create assignments for classes they are assigned to.