# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributors as noted in the CONTRIBUTORS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import account_type_required
from bson.objectid import ObjectId
from galah.db.models import Class, Assignment, Submission
from flask import render_template, request, abort
import datetime
from mongoengine import Q
from galah.web.util import create_time_element, GalahWebAdapter
import logging

logger = \
    GalahWebAdapter(logging.getLogger("galah.web.views.browse_assignments"))

@app.route("/assignments")
@account_type_required(("student", "teacher", "teaching_assistant"))
def browse_assignments():
    # Grab all the current user's classes
    classes = Class.objects(id__in = current_user.classes).only("name")

    # Get the current time so we don't have to do it over and over again.
    now = datetime.datetime.today()

    if "show_all" in request.args:
        assignments = list(Assignment.objects(
            Q(for_class__in = current_user.classes) &
            (Q(hide_until = None) | Q(hide_until__lt = now))
        ).only("name", "due", "due_cutoff", "for_class"))
    else:
        personal_deadlines = (current_user.personal_deadline.items() +
            current_user.personal_due_date.items())

        # Figure out which assignments the users have personal deadline
        # extensions first.
        due_date_exceptions = set()
        for k, v in personal_deadlines:
            if v > now - datetime.timedelta(weeks = 1):
                due_date_exceptions.add(ObjectId(k))
        due_date_exceptions = list(due_date_exceptions)

        assignments = list(Assignment.objects(
            Q(for_class__in = current_user.classes) &
            (Q(due__gt = now - datetime.timedelta(weeks = 1)) |
             Q(due_cutoff__gt = now - datetime.timedelta(weeks = 1)) |
             Q(id__in = due_date_exceptions)) &
            (Q(hide_until = None) | Q(hide_until__lt = now))
        ).only("name", "due", "due_cutoff", "for_class"))

    assignments = [i for i in assignments if
            not i.hide_until or i.hide_until < now]

    # Get the number of assignments that we could have gotten if we didn't
    # limit based on due date.
    all_assignments_count = Assignment.objects(
        Q(for_class__in = current_user.classes) &
        (Q(hide_until = None) | Q(hide_until__lt = now))
    ).count()

    submissions = list(Submission.objects(
            user = current_user.email,
            assignment__in = [i.id for i in assignments],
            most_recent = True
    ))

    # Add a property to all the assignments so the template can display their
    # respective class easier. Additionally, add a plain text version of the
    # due date
    for i in assignments:
        try:
            i.class_name = next((j.name for j in classes if j.id == i.for_class))
        except StopIteration:
            logger.error(
                "Assignment with id %s references non-existant class with id "
                "%s." % (str(i.id, i.for_class))
            )

            i.class_name = "DNE"

        i.apply_personal_deadlines(current_user)

        # Figure out the status messages that we want to display to the user.
        submitted = next((j for j in submissions if j.assignment == i.id), None)
        i.submitted = submitted
        i.status = i.status_color = None
        if submitted:
            i.status = (
                "You made a submission " +
                create_time_element(submitted.timestamp, now)
            )

            i.status_color = "#84B354"
        elif now < i.due:
            i.status = "You have not submitted yet"

            i.status_color = "#877150"
        elif now > i.due and i.due_cutoff and now > i.due_cutoff:
            i.status = "You have not submitted yet, and it is too late to do so"

            i.status_color = "#E9A400"
        elif now > i.due:
            i.status = "You have not submitted yet!"

            i.status_color = "#FB4313"

    # Sort the assignments by due_cutoff or due date if due_cutoff is not
    # assigned.
    assignments.sort(
        key = lambda i: i.due_cutoff if i.due_cutoff else i.due,
        reverse = True
    )

    return render_template(
        "assignments.html",
        assignments = assignments,
        hidden_assignments = -1 if "show_all" in request.args
                else all_assignments_count - len(assignments),
        create_time_element = create_time_element
    )
