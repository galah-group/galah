from mongoengine import *

#def rigidDocument(zdocClass):
    #def validate(self, *zargs, **zkwargs):
        #for k, v in vars(self).items():
            #if k.startswith("_"): continue
            
            #if k not in self._fields:
                #raise ValidationError("Extraneous attributes were found.")
        
        #return super(zdocClass, self).validate(*zargs, **zkwargs)

    #zdocClass.validate = validate
    
    #return zdocClass
        
#@rigidDocument
#class SubTest(EmbeddedDocument):
    #name = StringField(required = True)
    #score = FloatField()
    #max_score = FloatField()
    #message = StringField()
    #messages = ListField(StringField)

    #meta = {
        #"allow_inheritance": False
    #}

#@rigidDocument
#class TestResult(EmbeddedDocument):
    #sub_tests = ListField(EmbeddedDocumentField(SubTest))
    #score = FloatField()
    #max_score = FloatField()
    
    #meta = {
        #"allow_inheritance": False
    #}

class Submission(Document):
    assignment = ObjectIdField(required = True)
    user = StringField(required = True)
    timestamp = DateTimeField(required = True)
    marked_for_grading = BooleanField()
    most_recent = BooleanField()
    
    # Each filename should be a path relative to the root of the archive they
    # uploaded if they uploaded an archive, otherwise each filename should be
    # just the filename. Include extensions.
    uploaded_filenames = ListField(StringField())
    
    meta = {
        "allow_inheritance": False,
        "ordering": ["-timestamp"]
    }
