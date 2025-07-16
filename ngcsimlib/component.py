from ngcsimlib.context.contextObj import ContextObj
from ngcsimlib.context.contextObjectDecorators import component
from ngcsimlib.compartment.compartment import Compartment
from ngcsimlib.parser.utils import compilable
from typing import List, Tuple

@component
@compilable()
class Component(ContextObj):
    def __init__(self, name):
        super().__init__(name)

    @property
    def compartments(self) -> List[Tuple[str, Compartment]]:
        return [(n, v) for n, v in vars(self).items() if isinstance(v, Compartment)]
