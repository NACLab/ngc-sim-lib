from typing import Dict, Any

from .context_manager import global_context_manager as gcm
from .contextAwareObjectMeta import ContextAwareObjectMeta
from ngcsimlib._src.parser.utils import compileObject

class ContextAwareObject(object, metaclass=ContextAwareObjectMeta):
    """
    This is the base class for context-aware objects. It provides some methods
    that the context expects objects to have when they are registered with in
    the context. In general use this or one of its children when making custom
    components and objects to be used contexts.
    """
    def __init__(self, name: str):
        self.name = name
        self.context_path = gcm.current_path

    def to_json(self) -> Dict[str, Any]:
        """
        This method returns dictionary of data to be saved in the json file that
        will be used to rebuild this object.

        Returns: A dictionary of data that can be serialized by JSON.
        """
        data = {"args": self._args,
                "kwargs": self._kwargs}
        return data

    def compile(self):
        """
        A wrapper to compile this object, unless a custom compiler is being used
        do not modify this method.
        """
        compileObject(self)