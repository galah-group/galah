from galah.web import app
from flask.ext.login import current_user
from galah.web.auth import FlaskUser
from flask import redirect, url_for, request, abort, current_app, send_file
from galah.db.models import Archive
from bson.objectid import ObjectId, InvalidId

@app.route("/archives/<archive_id>")
def get_archive(archive_id):
	try:
		archive = Archive.objects.get(
			id = ObjectId(archive_id),
			archive_type = "assignment_package"
		)
	except InvalidId, Archive.DoesNotExist:
		app.logger.debug("Invalid ID: Malformed")

		abort(404)

	# If we can't find the archive return a 404 error.
	if archive is None:
		abort(404)

	# Ensure that the requesting user has permission to view this archive
	if not current_user.is_authenticated() or \
			archive.requester != current_user.email:
		return current_app.login_manager.unauthorized()

	if archive.error_string:
		raise RuntimeError(archive.error_string)
	else:
		return send_file(archive.file_location)