#!/usr/bin/env python

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

import sys
from galah.base.flockmail import FlockMessage, TestRequest, InternalTestRequest
from galah.base.zmqhelpers import router_send_json, router_recv_json
from flockmanager import FlockManager
from galah.db.models import (Submission, Assignment, TestHarness, TestResult,
                             User)
from bson.objectid import ObjectId
from bson.errors import InvalidId, InvalidDocument
import datetime

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("shepherd")

# Set up logging
import logging
logger = logging.getLogger("galah.shepherd")

# Connect to the mongo database
import mongoengine
mongoengine.connect(config["MONGODB"])

import zmq
context = zmq.Context()

# Socket to communicate with sheep over
sheep = context.socket(zmq.ROUTER)
sheep.bind(config["SHEEP_SOCKET"])

# Socket to communicate with other components
public = context.socket(zmq.DEALER)
public.bind(config["PUBLIC_SOCKET"])

def match_found(flock_manager, sheep_identity, request):
    logger.info(
        "Sending test request for submission [%s] to sheep [%s].",
        request.submission_id,
        repr(sheep_identity)
    )

    # Get submission and test harness to send to sheep
    submission = Submission.objects(id = request.submission_id).exclude(
        "most_recent",
        "uploaded_filenames"
    ).first()
    assignment = Assignment.objects.get(id = submission.assignment)
    test_harness = TestHarness.objects.get(id = assignment.test_harness)

    # Apply any personal deadlines to the assignment object.
    user = User.objects.get(email = submission.user)
    assignment.apply_personal_deadlines(user)

    data = {
        "assignment": assignment.to_dict(),
        "submission": submission.to_dict(),
        "test_harness": test_harness.to_dict()
    }

    router_send_json(
        sheep,
        sheep_identity,
        FlockMessage("request", data).to_dict()
    )

    return True

def main():
    flock = FlockManager(
        match_found,
        config["BLEET_TIMEOUT"],
        config["SERVICE_TIMEOUT"]
    )

    logger.info("Shepherd starting.")

    while True:
        # Wait until either the public or sheep socket has messages waiting
        zmq.select([public, sheep], [], [], timeout = 5)

        # Will grab all of the outstanding messages from the outside and place them
        # in the request queue
        while public.getsockopt(zmq.EVENTS) & zmq.POLLIN != 0:
            request = public.recv_json()
            logger.debug("Raw test request: %s", str(request))

            request = TestRequest.from_dict(request)
            try:
                submission = \
                    Submission.objects.get(id = ObjectId(request.submission_id))
            except Submission.DoesNotExist as e:
                logger.warning(
                    "Received test request for non-existant submission [%s].",
                    str(request.submission_id)
                )
                continue
            except bson.errors.InvalidId as e:
                logger.warning("Received malformed test request. %s", str(e))
                continue

            try:
                assignment = Assignment.objects.get(id = submission.assignment)
            except Assignment.DoesNotExist as e:
                logger.error(
                    "Received test request for a submission [%s] referencing "
                    "an invalid assignment [%s].",
                    str(submission.id),
                    str(submission.assignment)
                )
                continue

            if not assignment.test_harness:
                logger.warning(
                    "Received test request for a submission [%s] referencing "
                    "an assignment [%s] that does not have a test harness "
                    "associated with it.",
                    str(submission.id),
                    str(submission.assignment)
                )
                continue

            try:
                test_harness = \
                    TestHarness.objects.get(id = assignment.test_harness)
            except TestHarness.DoesNotExit as e:
                logger.error(
                    "Received test request for a submission [%s] referencing "
                    "an assignment [%s] that references a non-existant test "
                    "harness [%s].",
                    str(submission.id),
                    str(submission.assignment),
                    str(assignment.test_harness)
                )
                continue

            # Gather all the necessary information from the test request
            # received from the outside.
            processed_request = InternalTestRequest(
                submission.id,
                test_harness.config.get("galah/timeout",
                    config["BLEET_TIMEOUT"].seconds),
                test_harness.config.get("galah/environment", {})
            )

            logger.info("Received test request.")

            flock.received_request(processed_request)


        # Will grab all of the outstanding messages from the sheep and process them
        while sheep.getsockopt(zmq.EVENTS) & zmq.POLLIN != 0:
            try:
                sheep_identity, sheep_message = router_recv_json(sheep)
                sheep_message = FlockMessage.from_dict(sheep_message)
                logger.debug(
                    "Received message from sheep: %s",
                    str(sheep_message)
                )
            except ValueError as e:
                logger.error("Could not decode sheep's message: %s", str(e))
                logger.debug(
                    "Exception thrown while decoding sheep's message...",
                    exc_info = sys.exc_info()
                )
                continue

            if sheep_message.type == "distress":
                logger.warn("Received distress message. Sending bloot.")
                router_send_json(
                    sheep, sheep_identity, FlockMessage("bloot", "").to_dict()
                )

            elif sheep_message.type == "bleet":
                logger.debug(
                    "Sheep [%s] bleeted. Sending bloot.",
                    repr(sheep_identity)
                )

                result = flock.sheep_bleeted(sheep_identity)

                # Under certain circumstances we want to completely ignore a
                # bleet (see FlockManager.sheep_bleeted() for more details)
                if result is FlockManager.IGNORE:
                    logger.debug("Ignoring bleet.")
                    continue

                if not result:
                    router_send_json(
                        sheep,
                        sheep_identity,
                        FlockMessage("identify", "").to_dict()
                    )

                    logger.info(
                        "Unrecognized sheep [%s] connected, identify sent.",
                        repr(sheep_identity)
                    )

                    continue

                router_send_json(
                    sheep,
                    sheep_identity,
                    FlockMessage("bloot", "").to_dict()
                )
            elif sheep_message.type == "environment":
                if not flock.manage_sheep(sheep_identity, sheep_message.body):
                    logger.warn(
                        "Received environment from an already-recognized sheep."
                    )
            elif sheep_message.type == "result":
                logger.info("Received test result from sheep.")
                logger.debug(
                    "Received test result from sheep: %s",
                    str(sheep_message.body)
                )

                try:
                    submission_id = ObjectId(sheep_message.body["id"])

                    submission = Submission.objects.get(id = submission_id)

                    test_result = TestResult.from_dict(sheep_message.body)
                    try:
                        test_result.save()
                    except InvalidDocument:
                        logger.warn(
                            "Test result is too large for the database.",
                            exc_info = True
                        )
                        test_result = TestResult(failed = True)
                        test_result.save()

                    submission.test_results = test_result.id
                    submission.save()
                except (InvalidId, Submission.DoesNotExist) as e:
                    logger.warn(
                        "Could not retrieve submission [%s] for test result "
                        "received from sheep [%s].",
                        str(submission_id),
                        repr(sheep_identity)
                    )

                    continue

                router_send_json(
                    sheep,
                    sheep_identity,
                    FlockMessage(
                        "bloot", sheep_message.body["id"]
                    ).to_dict()
                )

                if not flock.sheep_finished(sheep_identity):
                    logger.info(
                        "Got result from sheep [%s] who was not processing "
                        "a test request.",
                        repr(sheep_identity)
                    )

        # Let the flock manager get rid of any dead or killed sheep.
        lost_sheep, killed_sheep = flock.cleanup()

        if lost_sheep:
            logger.warn(
                "%d sheep lost due to bleet timeout: %s",
                len(lost_sheep),
                str([repr(i) for i in lost_sheep])
            )

        if killed_sheep:
            logger.warn(
                "%d sheep lost due to request timeout: %s",
                len(killed_sheep),
                str([repr(i) for i in killed_sheep])
            )

if __name__ == "__main__":
    main()
