from collections import namedtuple
from threading import Thread
from galah.db.models import Archive, Submission
from galah.web import app
import datetime
import Queue
import tempfile
import os
import subprocess
import shutil

Task = namedtuple("Task", ("id", "requester", "assignment", "email"))

task_queue = Queue.Queue()

def _run():
    # The thread that executes this function should execute as a daemon,
    # therefore there is no reason to allow an explicit exit. It will be 
    # brutally killed once the app exits.
    archive_file = temp_directory = ""
    while True:
        # Block until we get a new task.
        task = task_queue.get()

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

        # This is the archive object we will eventually add to the database
        new_archive = Archive(
            id = task.id,
            requester = task.requester,
            archive_type = "assignment_package"
        )

        try:
            # Form the query
            query = {"assignment": task.assignment}

            # Only mention email in the query if it's not None or the empty
            # string, otherwise mongo will look for submissions that list the
            # user as None or the empty string (which should be exactly none of
            # the submission in the system).
            if task.email:
                query["user"] = task.email

            # Grab all the submissions
            submissions = list(
                Submission.objects(**query)
            )

            if not submissions:
                raise RuntimeError("No submissions found matching query.")

            # Organize all the submissions by user name, as this will closely
            # match the structure of the archive we will build.
            submission_map = {}
            for i in submissions:
                if i.user in submission_map:
                    submission_map[i.user].append(i)
                else:
                    submission_map[i.user] = [i]

            # Create a temporary directory we will create our archive in.
            temp_directory = tempfile.mkdtemp()

            # Create our directory tree. Instead of making new folders for each
            # submission and copying the user's files over however, we will
            # create symlinks to save space and time.
            for user, user_submissions in submission_map.items():
                # Create a directory for the user
                os.makedirs(os.path.join(temp_directory, user))

                # Create symlinks for all his submissions. Each symlink is
                # named after the submission date.
                for i in user_submissions:
                    time_stamp = i.timestamp.strftime("%Y-%m-%d-%H-%M-%S")
                    symlink_path = \
                        os.path.join(temp_directory, user, time_stamp)

                    # In the highly unlikely event that two of the same user's
                    # submissions have the same exact time stamp, we'll need to
                    # add a marker to the end of the timestamp.
                    marker = 0
                    while os.path.isfile(symlink_path +
                            ("-%d" % marker if marker > 0 else "")):
                        marker += 1

                    if marker > 0:
                        symlink_path += "-%d" % marker

                    # Create a symlink pointing to the actual submission
                    # directory with the name we gnerated
                    os.symlink(
                        os.path.join(app.config["SUBMISSION_DIRECTORY"], str(i.id)),
                        symlink_path
                    )

            # Create the actual archive file.
            # TODO: Create it in galah's /var/ directory
            archive_file = tempfile.mkstemp(suffix = ".tar.gz")[1]

            # Run tar and do the actual archiving. Will block until it's finished.
            subprocess.check_call(
                [
                    "tar", "--dereference", "--create", "--gzip", "--directory",
                    temp_directory, "--file", archive_file
                ] + submission_map.keys()
            )

            new_archive.file_location = archive_file

            new_archive.expires = \
                datetime.datetime.today() + datetime.timedelta(hours = 2)

            new_archive.save(force_insert = True)
        except Exception as e:
            app.logger.exception("An error occured while creating an archive.")

            # If we created a temporary archive file we need to delete it.
            new_archive.file_location = None
            if archive_file:
                os.remove(archive_file)

            new_archive.error_string = str(e)
            new_archive.save(force_insert = True)
        finally:
            if temp_directory:
                shutil.rmtree(temp_directory)

task_thread = Thread(name = "task_thread", target = _run)
task_thread.daemon = True
task_thread.start()

def add_task(task):
    task_queue.put(task)

    global task_thread
    if not task_thread or not task_thread.is_alive():
        if task_thread:
            app.logger.warning(
                "task_thread death detected, restarting task_thread."
            )

        task_thread = Thread(name = "task_thread", target = _run)
        task_thread.daemon = True
        task_thread.start()

def queue_size():
    return task_queue.qsize()