from mongoengine import *
import datetime

class TestDescription(EmbeddedDocument):
    title = StringField(required = True)
    description = StringField()
    
    meta = {
        "allow_inheritance": False
    }

class TestSpecification(EmbeddedDocument):
    test_driver = StringField(required = True)
    timeout = IntField(default = 30)
    actions = ListField(StringField())
    config = DictField()
    
    meta = {
        "allow_inheritance": False
    }

class Assignment(Document):
    name = StringField(required = True)
    due = DateTimeField(required = True)
    due_cutoff = DateTimeField()
    hide_until = DateTimeField(default = datetime.datetime.min, required = True)
    for_class = ObjectIdField(required = True)
    
    # English description of each of the tests
    tests = ListField(EmbeddedDocumentField(TestDescription))
    
    # Rigid specification used by the shepherd to craft a test request
    test_specification = EmbeddedDocumentField(TestSpecification)

    meta = {
        "allow_inheritance": False
    }

    def validate(self):
        if self.due_cutoff and self.due > self.due_cutoff:
            raise ValidationError("due cannot be later than due_cutoff")

        return Document.validate(self)