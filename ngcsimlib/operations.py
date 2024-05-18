from abc import abstractmethod

class BaseOp():
    is_compilable = True

    @staticmethod
    @abstractmethod
    def operation(*sources):
        pass

    def compile(self, arg_order):
        inputs, output = self.parse()
        iids = [str(i) for i in inputs]

        def _op_compiled(*args):
            op_args = [args[arg_order.index(narg)] for narg in iids]
            return self.operation(*op_args)

        return _op_compiled, output

    def parse(self):
        assert self.is_compilable
        inputs = []
        for s in self.sources:
            if isinstance(s, BaseOp):
                inputs.append(s.parse())
            else:
                inputs.append(s._uid)
        return inputs, self.destination._uid if self.destination is not None else None

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
