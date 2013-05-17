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

# Load up the configuration for the email validation regular expression
from galah.base.config import load_config
config = load_config("global")

class User(Document):
    email = EmailField(unique = True, primary_key = True,
                       regex = config["EMAIL_VALIDATION_REGEX"])
    seal = StringField()
    account_type = StringField(choices = ["student", "teaching_assistant",
                                          "teacher", "admin"], required = True)
    classes = ListField(ObjectIdField())

    # The individual cutoff date
    personal_deadline = MapField(DateTimeField())

    # The individual due date
    personal_due_date = MapField(DateTimeField())

    meta = {
        "indexes": ["email", "classes"],
        "allow_inheritance": False
    }
