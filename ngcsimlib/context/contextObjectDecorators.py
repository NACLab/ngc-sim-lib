from ngcsimlib.logger import warn
from .context import ContextObjectTypes

class ContextObjectDecorators:
    @staticmethod
    def component(cls):
        cls._type = ContextObjectTypes.component

        if not hasattr(cls, "to_json"):
            warn(f"Component class {cls.__name__} has no \"to_json\" method and "
                 f"therefore will not be able to be saved properly")

        return cls



component = ContextObjectDecorators.component