from galah.web import app
from galah.web.auth import account_type_required
from galah.db.models import Assignment, Submission, Archive
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import send_file, abort
from flask.ext.login import current_user
import os.path
import subprocess
import tempfile
import datetime

@app.route("/assignments/<assignment_id>/<submission_id>/download.tar.gz")
@account_type_required(("student", "teacher"))
def download_submission(assignment_id, submission_id):
    # Figure out which assignment the user asked for.
    try:
        assignment_id = ObjectId(assignment_id)
        assignment = Assignment.objects.get(id = assignment_id)
    except InvalidId, Assignment.DoesNotExist:
        app.logger.exception("Could not retrieve assignment.")
        
        abort(404)

    # Figure out which submission the user is trying to download
    try:
        submission_id = ObjectId(submission_id)
        submission = Submission.objects.get(id = submission_id)
    except InvalidId, Submission.DoesNotExist:
        app.logger.exception("Could not retrieve submission.")

        abort(404)

    # Find any expired archives and remove them
    for i in Archive.objects(expires__lt = datetime.datetime.today()):
        if i.file_location:
            app.logger.debug("Erasing old archive at '%s'." % i.file_location)

            try:
                os.remove(i.file_location)
            except OSError:
                app.logger.exception(
                    "Could not remove expired archive at %s." %
                        i.file_location
                )

        i.delete()

    new_archive = Archive(
        requester = current_user.id,
        archive_type = "single_submission"
    )

    archive_file = ""
    try:
        # Create the actual archive file.
        # TODO: Create it in galah's /var/ directory
        archive_file = tempfile.mkstemp(suffix = ".tar.gz")[1]

        # Run tar and do the actual archiving. Will block until it's finished.
        subprocess.check_call(
            [
                "tar", "--dereference", "--create", "--gzip", "--directory",
                os.path.join(app.config["SUBMISSION_DIRECTORY"], str(submission_id)),
                "--file", archive_file
            ] + submission.uploaded_filenames
        )

        new_archive.file_location = archive_file

        new_archive.expires = \
                datetime.datetime.today() + datetime.timedelta(minutes = 10)

        new_archive.save(force_insert = True)

        return send_file(archive_file)
    except Exception as e:
        app.logger.exception("An error occured while creating an archive.")

        # If we created a temporary archive file we need to delete it.
        new_archive.file_location = None
        if archive_file:
            os.remove(archive_file)

        new_archive.error_string = str(e)
        new_archive.save(force_insert = True)

        abort(500)