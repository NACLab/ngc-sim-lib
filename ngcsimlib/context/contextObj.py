from ._context_manager import get_current_path
from .contextObjectMeta import ContextObjectMeta

class ContextObj(object, metaclass=ContextObjectMeta):
    def __init__(self, name: str):
        self.name = name
        self.context_path = get_current_path()

    def to_json(self):
        data = {"args": self._args,
                "kwargs": self._kwargs}
        return data

    def get_module_data(self):
        cls = self.__class__.__name__
        c_mod = self.__class__.__module__
        return {"cls": cls,
                "module": c_mod}