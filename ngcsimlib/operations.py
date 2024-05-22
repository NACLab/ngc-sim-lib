from abc import abstractmethod

class BaseOp():
    is_compilable = True

    @staticmethod
    @abstractmethod
    def operation(*sources):
        pass

    def __init__(self, *sources):
        self.sources = sources
        self.destination = None

    def __call__(self, *args, **kwargs):
        self.resolve(self.value)

    def set_destination(self, destination):
        self.destination = destination

    @property
    def value(self):
        return self.operation(*[s.value for s in self.sources])

    def resolve(self, value):
        if self.destination is not None:
            self.destination.set(value)

    def dump(self):
        class_name = self.__class__.__name__

        source_array = []
        for source in self.sources:
            if isinstance(source, BaseOp):
                source_array.append(source.dump())
            else:
                source_array.append(source.name)

        destination = self.destination.name if self.destination is not None else None


        return {"class": class_name, "sources": source_array, "destination": destination}
    def __repr__(self) -> str:
        line = f"[OP:{self.__class__.__name__}]"
        if len(self.sources) > 0:
            line += f"\tSources: {[source for source in self.sources]}"
        if self.destination is not None:
            line += f"\tDestination: {self.destination.name}"
        return line

class summation(BaseOp):
    @staticmethod
    def operation(*sources):
        s = None
        for source in sources:
            if s is None:
                s = source
            else:
                s += source
        return s

class negate(BaseOp):
    @staticmethod
    def operation(*sources):
        return -sources[0]



class add(summation):
    is_compilable = False
    def resolve(self, value):
        if self.destination is not None:
            self.destination.set(self.destination.value + value)

class overwrite(BaseOp):
    @staticmethod
    def operation(*sources):
        return sources[0]
