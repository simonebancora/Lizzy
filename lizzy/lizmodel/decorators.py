def copy_doc(from_method):
    def decorator(to_method):
        to_method.__doc__ = from_method.__doc__
        return to_method
    return decorator