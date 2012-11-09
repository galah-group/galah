modify_assignment
=================

Modifies an existing assignment.

Reference
---------

.. function:: modify_assignment(id[, name = '', due = '', for_class = '', due_cutoff = '', hide_until = '']):

    :param id: The ID of the assignment to modify.

    :param name: The new name of the assignment, may be blank to leave the
                 original name unchanged.

    :param due: The new due date of the assignment, ex: "10/20/2012 10:09:00".
                may be blank to leave the original due date unchanged.

    :param for_class: The new ID or partial name of the class the assignment is
                      for. May be left blank to leave the original class
                      unchanged.

    :param due_cutoff: The new cutoff date of the assignment. Same format as
                       the due date. May be left blank to leave the original
                       value unchanged. If ``none`` is specified, the previous
                       cutoff date is removed.

    :param hide_until: If specified, the assignment will not be visible to users
                       until this time. If ``none`` is specified, the previous
                       hide-until date is removed.

    :raises RuntimeError: If the assignment could not be found.
    
    :raises RuntimeError: If current_user is not a teacher of the new for_class
                          or the original and not an admin.

Example Usage
-------------

Here we will rename an assignment named **World Domination** to
**Local Domination**.

>>> modify_assignment 50907cca55c4481a5027103c "Local Domination"
--Logged in as jsull003@ucr.edu--
Success! The following changes were applied to Assignment [id = 50907cca55c4481a5027103c, name = World Domination].
	Name changed from 'World Domination' to 'Local Domination'.

Now we will change that same assignment back to **World Domination**, change its
due date, change what class it's for, and add a cutoff date.

>>> modify_assignment 50907cca55c4481a5027103c "World Domination Domination" "12/01/2012 23:59:59" "CS 10" "12/02/2012 23:59:59"
--Logged in as jsull003@ucr.edu--
Success! The following changes were applied to Assignment [id = 50907cca55c4481a5027103c, name = Local Domination].
	Name changed from 'Local Domination' to 'World Domination Domination'.
	Due date changed from '2012-10-20 10:12:00' to '2012-12-01 23:59:59'.
	Cutoff date changed from 'None' to '2012-12-01 23:59:59'.
	Class changed from Class [id = 5090634855c448134f67b3e3, name = CS 9000] to Class [id = 509066e855c448134f67b3e4, name = CS 10].

Permissions
-----------

**admin** users and **teacher** users can use this command. Teacher users can
only use this command on assignments for classes they are assigned to.