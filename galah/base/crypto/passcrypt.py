from collections import namedtuple
import os
import pbkdf2

# The known algorithms
algorithms = ("pbkdf2", )

# A hash along with all the information used to create it
HashSeal = namedtuple("HashSeal", ("hash", "algorithm", "salt", "cost_factor"))

def hash(password, algorithm, salt, cost_factor, **kwargs):
    """
    Returns a hashed password (not a HashSeal) in binary format.
    
    **kwargs are passed to the underlying hash function unchanged.
    
    """
    
    if algorithm == "pbkdf2":
        return pbkdf2.pbkdf2_bin(str(password), salt, cost_factor, **kwargs)
    else:
        raise ValueError("algorithm: Specified algorithm is not recognized.")

def seal(password, algorithm = "pbkdf2", salt = None, cost_factor = 1000):
    "Returns a HashSeal of the given password."
    
    if salt is None:
        salt = os.urandom(4)
        
    return HashSeal(
        hash = hash(password, algorithm, salt, cost_factor),
        algorithm = algorithm,
        salt = salt,
        cost_factor = cost_factor
    )
    
def check_seal(password, seal):
    "Returns True if a password is the password used to create the given seal."
    
    def safeStrCmp(a, b):
        if len(a) != len(b):
            return False
        
        rv = True
        for x, y in zip(a, b):
            if x != y:
                rv = False
        
        return rv
    
    # Create the hash of the password we will check against the seal. Note its
    # important that password is a string (not unicode) because ord() needs to
    # work with it.
    check_hash = hash(password, seal.algorithm, seal.salt, seal.cost_factor)
    
    return safeStrCmp(check_hash, seal.hash)
    
def serialize_seal(seal):
    return ";".join((
        seal.hash.encode("hex"), 
        seal.algorithm, 
        seal.salt.encode("hex"), 
        str(seal.cost_factor)
    ))

def deserialize_seal(seal):
    parts = seal.split(";")
    parts[0] = str(parts[0].decode("hex"))
    parts[1] = unicode(parts[1])
    parts[2] = str(parts[2].decode("hex"))
    parts[3] = int(parts[3])
    
    return HashSeal(*parts)

if __name__ == "__main__":
    test_seal = seal("test")
    print test_seal
    
    assert check_seal("test", test_seal)
    
    print serialize_seal(test_seal), deserialize_seal(serialize_seal(test_seal))
    assert deserialize_seal(serialize_seal(test_seal)) == test_seal
