from galah.web.galahweb import app
from flask.ext.login import current_user
from galah.web.galahweb.auth import account_type_required
from galah.db.models import Class, Assignment, Submission
from flask import render_template, request
import datetime
from mongoengine import Q
from galah.web.galahweb.util import create_time_element

@app.route("/assignments")
@account_type_required(("student", "teacher"))
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
        assignments = list(Assignment.objects(
            Q(for_class__in = current_user.classes) &
            (Q(due__gt = now - datetime.timedelta(weeks = 1)) |
            Q(due_cutoff__gt = now - datetime.timedelta(weeks = 1))) &
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
            app.logger.error("Assignment with id %s references non-existant "
                             "class with id %s." % (str(i.id, i.for_class)))
            
            i.class_name = "DNE"

        # Figure out the status messages that we want to display to the user.
        submitted = next((j for j in submissions if j.assignment == i.id), None)
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
