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

    def __repr__(self) -> str:
        return f"[OP:summation] {[source.name for source in self.sources]}"

class negate(BaseOp):
    @staticmethod
    def operation(*sources):
        return -sources[0]

    def __repr__(self) -> str:
        return f"[OP:negate] {self.sources[0].name}"

class add(summation):
    is_compilable = False
    def resolve(self, value):
        if self.destination is not None:
            self.destination.set(self.destination.value + value)

class overwrite(BaseOp):
    @staticmethod
    def operation(*sources):
        return sources[0]

    def __repr__(self) -> str:
        return f"[OP:overwrite] {self.sources[0].name}"