from ngcsimlib.operations import BaseOp, overwrite
import uuid

All_compartments = {}

class Compartment():
    @classmethod
    def is_compartment(cls, obj):
        return hasattr(obj, "_is_compartment")

    def __init__(self, initial_value=None, static=False, name="default"):
        self._is_compartment = True
        self.__add_connection = None
        self._static = static
        self.value = initial_value
        self._uid = uuid.uuid4()
        All_compartments[str(self._uid)] = self
        self.name = name

    def _setup(self, add_connection):
        self.__add_connection = add_connection

    def set(self, value):
        if not self._static:
            self.value = value
        else:
            raise RuntimeError("Can not assign value to static compartment")

    def __repr__(self):
        return f"[{self.name}] {repr(self.value)}"

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
