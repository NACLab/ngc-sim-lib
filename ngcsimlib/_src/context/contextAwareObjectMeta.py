from ngcsimlib.logger import error, warn
from .context_manager import global_context_manager as gcm
from collections.abc import Iterable

class ContextAwareObjectMeta(type):
    """
    This is the metaclass for objects that want to interact with the context
    they were created in. Generally use the base class "ContextAwareObject" over
    this metaclass.
    """
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)

        obj._args = args
        obj._kwargs = kwargs

        if not hasattr(obj, 'name'):
            error(f"Created context objects must have a name. "
                  f"Error occurred when making an object of class {cls.__name__}")

        contextRef = gcm.current_context
        if contextRef is None:
            warn(f"An instance of a context aware object was initialized while "
                 f"the current context is None. Did you forget to place it in "
                 f"a \"with\" block?")
            return obj

        contextRef.registerObj(obj)

        if hasattr(obj, "compartments") and isinstance(obj.compartments, Iterable) and not isinstance(obj.compartments, (str, bytes)):
            for (comp_name, comp) in obj.compartments:
                if hasattr(comp, "_setup") and callable(comp._setup):
                    comp._setup(obj.name, comp_name, gcm.current_path)

        return obj
