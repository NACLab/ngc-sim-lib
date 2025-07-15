from abc import abstractmethod, ABC
from ngcsimlib.logger import warn


class BaseOp(ABC):
    """
    This is the base class for all operations that define cable behavior in
    ngcsimlib. Generally the there is one governing design principal that
    should be followed when building new  operations. The first is
    determining if this operation should be able to be compiled to be used in
    ngcsimlib's compiled commands, if it can be that will restrict the design
    pattern that can be used.

    For commands that can be compiled using ngcsimlib's compiler, all their
    operational logic must be contained inside the subclass's operation
    method. This also means that the transition method that is defined on the
    base class should not be overwritten.

    For commands that do not need to be compiled using ngcsimlib's compiler
    they do not have this restriction but their flag of `is_compilable` needs
    to be set to false or undefined  behavior may happen if they are
    attempted to be compiled. It is important to note that any command that
    has connections using uncompilable ops can not be compiled.
    """
    pass