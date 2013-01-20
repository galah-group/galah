# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
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
from flask import abort, render_template, get_flashed_messages, request
from galah.db.models import Assignment, Submission, TestResult, User
from galah.base.pretty import pretty_time
from galah.web.util import create_time_element, GalahWebAdapter
import datetime
import logging

# Load Galah's configuration
from galah.base.config import load_config
config = load_config("web")

logger = GalahWebAdapter(logging.getLogger("galah.web.views.view_assignment"))

@app.route("/assignments/<assignment_id>/")
@account_type_required(("student", "teacher"))
def view_assignment(assignment_id):
    simple_archive_form = SimpleArchiveForm()

    # Convert the assignment in the URL into an ObjectId
    try:
        id = ObjectId(assignment_id)
    except InvalidId:
        logger.info("Invalid Assignment ID requested.")

        abort(404)

    # Retrieve the assignment
    try:
        assignment = Assignment.objects.get(id = id)
    except Assignment.DoesNotExist:
        logger.info("Non-extant ID requested.")

        abort(404)

    # Teachers and students have different default browsing view.
    view_as = current_user.account_type

    # Teachers are able to browse as students by request.
    if view_as == "teacher" and "as_student" in request.args:
        view_as = "student"

    # Get all of the submissions for this assignment    
    user_count = 1
    if view_as == "teacher":
        submissions = list(
            Submission.objects(
                assignment = id,
                most_recent = True
            ).order_by(
                "-most_recent",
                "-timestamp"
            )
        )
        user_count = User.objects(
            account_type = "student",
            classes = assignment.for_class
        ).count()
    else:
        submissions = list(
            Submission.objects(
                user = current_user.id,
                assignment = id
            ).order_by(
                "-most_recent",
                "-timestamp"
            )
        )

    test_results = list(
        TestResult.objects(
            id__in = [i.test_results for i in submissions if i.test_results]
        )
    )

    # Match test results to submissions
    for i in submissions:
        for j in test_results:
            if i.test_results == j.id:
                i.test_results_obj = j

    # Current time to be compared to submission test_request_timestamp
    now = datetime.datetime.now()

    # Add the pretty version of each submissions timestamp
    for i in submissions:
        i.timestamp_pretty = pretty_time(i.timestamp)

        # If the user submitted a test request and there aren't any results
        if (i.test_request_timestamp and not i.test_results):
            timedelta = now - i.test_request_timestamp
            i.show_resubmit = (timedelta > config["STUDENT_RETRY_INTERVAL"])

    # Use different template depending on who the assignment is being viewed by
    template = "assignment.html" if view_as == "student" \
        else "assignment_stats.html"

    return render_template(
        template,
        now = datetime.datetime.today(),
        create_time_element = create_time_element,
        assignment = assignment,
        submissions = submissions,
        simple_archive_form = simple_archive_form,
        users = user_count,
        new_submissions = [v for k, v in get_flashed_messages(with_categories = True) if k == "new_submission"]
    )
