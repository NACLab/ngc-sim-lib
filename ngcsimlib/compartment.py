from ngcsimlib.operations import BaseOp, overwrite
from ngcsimlib.utils import Set_Compartment_Batch, get_current_path
import uuid


class Compartment:
    @classmethod
    def is_compartment(cls, obj):
        return hasattr(obj, "_is_compartment")

    def __init__(self, initial_value=None, static=False):

        self._is_compartment = True
        self.__add_connection = None
        self._static = static
        self.value = initial_value
        self._uid = uuid.uuid4()
        self.name = None
        self.path = None

    def _setup(self, current_component, key):
        self.__add_connection = current_component.add_connection
        self.name = current_component.name + "/" + key
        self.path = get_current_path() + "/" + self.name
        Set_Compartment_Batch({str(self.path): self})

    def set(self, value):
        if not self._static:
            self.value = value
        else:
            raise RuntimeError("Can not assign value to static compartment")

    def clamp(self, value):
        self.set(value)

    def __repr__(self):
        return f"[{self.name}]"

    def __str__(self):
        return str(self.value)

    def __lshift__(self, other) -> None:
        if isinstance(other, BaseOp):
            other.set_destination(self)
            self.__add_connection(other)
        else:
            op = overwrite(other)
            op.set_destination(self)
            self.__add_connection(op)
