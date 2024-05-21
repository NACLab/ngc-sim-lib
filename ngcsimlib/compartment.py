from ngcsimlib.operations import BaseOp, overwrite
import uuid

#Note these are to get a copied hash table of values not the actual compartments
__all_compartments = {}
def Get_Compartment_Batch(compartment_uids=None):
    if compartment_uids is None:
        return {key: c.value for key, c in __all_compartments.items()}
    return {key: __all_compartments[key].value for key in compartment_uids}

def Set_Compartment_Batch(compartment_map=None):
    if compartment_map is None:
        return

    for key, value in compartment_map.items():
        if key not in __all_compartments.keys():
            __all_compartments[key] = value
        else:
            __all_compartments[key].set(value)


class Compartment:
    @classmethod
    def is_compartment(cls, obj):
        return hasattr(obj, "_is_compartment")

    def __init__(self, initial_value=None, static=False, name="default"):
        self._is_compartment = True
        self.__add_connection = None
        self._static = static
        self.value = initial_value
        self._uid = uuid.uuid4()
        Set_Compartment_Batch({str(self._uid): self})
        self.name = name

    def _setup(self, add_connection):
        self.__add_connection = add_connection

    def set(self, value):
        if not self._static:
            self.value = value
        else:
            raise RuntimeError("Can not assign value to static compartment")

    def clamp(self, value):
        self.set(value)

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
