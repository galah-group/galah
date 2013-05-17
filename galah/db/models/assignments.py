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

from mongoengine import *
import datetime

class TestHarness(Document):
    # The harness's user-defined configuration. May contain any key value pairs,
    # but certain pairs have special meaning:
    #    * "galah/TIMEOUT" is the number of seconds to allow the test harness to
    #      run before the entire VM is brutally destroyed.
    #    * "galah/ENVIRONMENT" is a dictionary that explains the environment
    #      that the VM must have.
    config = DictField()

    # The directory on the filesystem that has the test harness stored within it.
    harness_path = StringField(required = True)

    meta = {
        "allow_inheritance": False
    }

    def to_dict(self):
        return {
            "config": self.config,
            "harness_path": self.harness_path,
            "id": str(self.id)
        }

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    due_cutoff = DateTimeField()
    hide_until = DateTimeField(default = datetime.datetime.min, required = True)
    for_class = ObjectIdField(required = True)
    test_harness = ObjectIdField()
    allow_final_submission = BooleanField(default = True)

    meta = {
        "allow_inheritance": False
    }

    def to_dict(self):
        return {
            "name": self.name,
            "due": self.due.isoformat(),
            "due_cutoff":
                None if not self.due_cutoff else self.due_cutoff.isoformat(),
            "hide_until": str(self.for_class),
            "test_harness": str(self.test_harness)
        }

    def validate(self):
        if self.due_cutoff and self.due > self.due_cutoff:
            raise ValidationError("due cannot be later than due_cutoff")

        return Document.validate(self)

    def apply_personal_deadlines(self, user):
        self.due_cutoff = user.personal_deadline.get(
            str(self.id), self.due_cutoff
        )

        self.due = user.personal_due_date.get(
            str(self.id), self.due
        )
