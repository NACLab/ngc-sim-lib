
def priority(value=None):
    def decorator(fn):
        fn._priority = value
        return fn
    return decorator
