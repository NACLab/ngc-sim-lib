
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
    A helper method for getting a context by a provided path
    """
    return __contexts.get(__current_context + "/" + path, None)


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
