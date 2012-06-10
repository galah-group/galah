import os, subprocess, errno, shutil
from bson.objectid import ObjectId

class FileStore:
    """
    This store should only be used if all of Galah is contained on a single
    server!
    
    """
    
    submissionDirectory = "/var/local/galah-web/submissions/"
    prefix = "file://"
    
    def store(self, zobject, ztestables, zoverwrite = False):
        """
        ztestables must be an archive

        """
        
        if not zobject.id:
            zobject.id = ObjectId()
        
        # Ensure that we have an absolute path so the decompression programs
        # don't have a fit.
        testables = os.path.abspath(ztestables)
        
        # Figure out where we will store this submission
        directory = os.path.join(
            FileStore.submissionDirectory, str(zobject.id)
        )
        
        # Create the directories needed (this will try to create the entire
        # directory tree if necessary).
        try:
            os.makedirs(directory)
        except OSError as e:
            if zoverwrite and e.errno == errno.EEXIST:
                # If we need to overwrite the directory delete it and then
                # create it anew
                shutil.rmtree(directory)
                os.makedirs(directory)
            else:
                raise
        
        try:
            # Decompress the archive
            if ztestables.endswith(".tar.gz"):
                subprocess.check_call(["tar", "xf", ztestables], cwd = directory)
            elif ztestables.endswith(".zip"):
                subprocess.check_call(["unzip", ztestables], cwd = directory)
            else:
                raise ValueError("ztestables is not a valid archive")
        except:
            try:
                os.rmdir(directory)
            except OSError:
                pass
            
            raise
            
        return FileStore.prefix + directory
    
    @staticmethod
    def canHandle(self, zsource):
        return zsource.startswith(FileStore.prefix)    
    
    def load(self, zobject):
        source = zobject.testables
        
        if not FileStore.canHandle(source):
            raise ValueError("cannot open zobject")
            
        return source[len(FileStore.prefix):]
        
    
