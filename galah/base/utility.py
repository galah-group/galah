def tuplify(target):
    "Transforms a single item into a tuple if it is not already a tuple."

    if type(target) is not tuple:
        return (target, )
    else:
        return target