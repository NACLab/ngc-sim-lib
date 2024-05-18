from abc import abstractmethod

class BaseOp():
    is_compilable = True

    @staticmethod
    @abstractmethod
    def operation(*sources):
        pass

    def compile(self):
        assert self.is_compilable
        inputs = []
        for s in self.sources:
            if isinstance(s, BaseOp):
                inputs.append(s.compile())
            else:
                inputs.append(s._uid)
        return self.operation, inputs, \
            self.destination._uid if self.destination is not None else None

    def __repr__(self) -> str:
        return f"[OP:overwrite] {self.sources[0].name}"

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

class negate(BaseOp):
    @staticmethod
    def operation(*sources):
        return -sources[0]

class add(BaseOp):
    @staticmethod
    def operation(*sources):
        s = None
        for source in sources:
            if s is None:
                s = source
            else:
                s += source
        return s

    def resolve(self, value):
        if self.destination is not None:
            self.destination.set(self.destination.value + value)

class overwrite(BaseOp):
    @staticmethod
    def operation(*sources):
        return sources[0]