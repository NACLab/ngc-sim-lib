
## Contexts
__current_context = ""
__contexts = {"": None}

def get_current_context():
    """
    A helper method for getting the current active context object
    """
    return __contexts[__current_context]


def get_current_path():
    """
    A helper method for getting the current context path
    """
    return __current_context


def get_context(path):
    """
    A helper method for getting a context by a provided path, to search from the
    root path start the path with '/'
    """
    if path[0] == "/":
        return __contexts.get(path, None)

    return __contexts.get(__current_context + "/" + path, None)


def infer_context(path, trailing_path=1):
    """
    A helper method that attempts to get the given context by a provided path, if
    the context does not exist it will return the current context
    Args:
        path: path to where the context should be
        trailing_path: how many trailing path locations should be ignored in
        general 1 for components, 2 for compartments


    Returns: located context object or the current context if unable to locate
    given context
    """
    ctx = get_context("/".join(path.split("/")[:-trailing_path]))

    if ctx is None:
        return get_current_context()
    return ctx

def add_context(name, con):
    """
    A helper method for adding a context to the current path
    """
    __contexts[__current_context + "/" + name] = con


def set_new_context(path):
    """
    A helper method for updating the current active context
    """
    global __current_context
    __current_context = path
