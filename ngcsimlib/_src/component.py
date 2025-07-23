from ngcsimlib._src.context.contextAwareObject import ContextAwareObject
from ngcsimlib._src.context.contextObjectDecorators import component
from ngcsimlib._src.compartment.compartment import Compartment
from ngcsimlib._src.parser.utils import compilable
from typing import List, Tuple, Dict, Any


@component
@compilable
class Component(ContextAwareObject):
    """
    Component is a base class of context aware objects that are also specially
    tracked by contexts. They are expected to make up a large amount of
    user-defined classes as they will be the various parts of models.
    """
    def __init__(self, name):
        super().__init__(name)

    @property
    def compartments(self) -> List[Tuple[str, Compartment]]:
        """
        It is expected that components will have compartments, and this allows
        for easy iteration over all the compartments in a component.
        Returns: a list of compartments found on this component
        """
        return [(n, v) for n, v in vars(self).items() if isinstance(v, Compartment)]
