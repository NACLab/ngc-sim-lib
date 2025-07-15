def compilable(fn):
    fn._is_compilable = True
    return fn