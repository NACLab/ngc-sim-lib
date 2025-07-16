from ngcsimlib.logger import error, warn
from ._context_manager import get_current_context, get_current_path
from collections.abc import Iterable

class ContextObjectMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)

        obj._args = args
        obj._kwargs = kwargs

        if not hasattr(obj, 'name'):
            error(f"Created context objects must have a name. "
                  f"Error occurred when making an object of class {cls.__name__}")

        contextRef = get_current_context()
        if contextRef is None:
            warn(f"An instance of a context aware object was initialized while "
                 f"the current context is None. Did you forget to place it in "
                 f"a \"with\" block?")
            return obj

        contextRef.registerObj(obj)

        if hasattr(obj, "compartments") and isinstance(obj.compartments, Iterable) and not isinstance(obj.compartments, (str, bytes)):
            for (comp_name, comp) in obj.compartments:
                if hasattr(comp, "_setup") and callable(comp._setup):
                    comp._setup(obj.name, comp_name, get_current_path())

        return obj
