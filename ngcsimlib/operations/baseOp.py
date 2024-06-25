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
    method. This also means that the resolve  method that is defined on the
    base class should not be overwritten.

    For commands that do not need to be compiled using ngcsimlib's compiler
    they do not have this restriction but their flag of `is_compilable` needs
    to be set to false or undefined  behavior may happen if they are
    attempted to be compiled. It is important to note that any command that
    has connections using uncompilable ops can not be compiled.
    """
    is_compilable = True

    @staticmethod
    @abstractmethod
    def operation(*sources):
        """
        The operation function is the location of all the runtime logic for
        the operation. It is a pure function that
        only has access to the source values at runtime.

        Args:
            *sources: a list of values from all source connections (In the
            order they are in the constructor)

        Returns:
            the computed value to be resolved
        """
        pass

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        if not hasattr(value, "_is_compartment"):
            warn(
                f"Failed to add \"{value}\" as a destination as it is "
                f"not a compartment.")
        else:
            self._destination = value


    def __init__(self, *sources):
        self.sources = sources
        self._destination = None

    def __call__(self, *args, **kwargs):
        self.resolve(self.value)

    def set_destination(self, destination):
        self.destination = destination

    @property
    def value(self):
        return self.operation(*[s.value for s in self.sources])

    def resolve(self, value):
        """
        The base resolver for operations, if this is modified those
        modifications will not be reflected in compiled
        operations as this is never called by a compiled method

        Args:
            value: the result of the operation's operation method
        """
        if self.destination is not None:
            self.destination.set(value)

    def dump(self):
        """
        dumps the operation to a json format

        Returns:
            The json format for the operation
        """
        class_name = self.__class__.__name__

        source_array = []
        for source in self.sources:
            if isinstance(source, BaseOp):
                source_array.append(source.dump())
            else:
                source_array.append(source.name)

        destination = self.destination.name if self.destination is not None \
            else None

        return {"class": class_name, "sources": source_array,
                "destination": destination}

    def __repr__(self) -> str:
        line = f"[OP:{self.__class__.__name__}]"
        if len(self.sources) > 0:
            line += f"\tSources: {[source for source in self.sources]}"
        if self.destination is not None:
            line += f"\tDestination: {self.destination.name}"
        return line
