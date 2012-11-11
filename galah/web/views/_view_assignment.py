## Create the form that takes simple archives ##
from flask.ext.wtf import Form, FieldList, FileField, validators, BooleanField

class SimpleArchiveForm(Form):
    archive = FieldList(FileField("Archive"), min_entries = 3)
    
## The Actual View ##
from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import account_type_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort, render_template, get_flashed_messages
from galah.db.models import Assignment, Submission
from galah.base.pretty import pretty_time
from galah.web.util import create_time_element
import datetime

@app.route("/assignments/<assignment_id>/")
@account_type_required(("student", "teacher"))
def view_assignment(assignment_id):
    simple_archive_form = SimpleArchiveForm()
    
    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        app.logger.debug("Invalid ID (%s)" % str(id))
        
        abort(404)
    
    # Retrieve the assignment
    try:
        assignment = Assignment.objects.get(id = id)
    except Assignment.DoesNotExist:
        app.logger.debug("Non-extant ID (%s)" % str(id))
        
        abort(404)
    
    # Get all of the submissions for this assignmnet
    submissions = list(Submission.objects(user = current_user.id, assignment = id))
    
    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)
    
    return render_template(
        "assignment.html",
        now = datetime.datetime.today(),
        create_time_element = create_time_element,
        assignment = assignment, 
        submissions = submissions,
        simple_archive_form = simple_archive_form,
        new_submissions = [v for k, v in get_flashed_messages(with_categories = True) if k == "new_submission"]
    )
