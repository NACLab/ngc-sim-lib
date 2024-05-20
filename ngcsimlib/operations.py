from abc import abstractmethod

class BaseOp():
    is_compilable = True

    @staticmethod
    @abstractmethod
    def operation(*sources):
        pass

    def compile(self, arg_order):
        exc_order = []
        ops = []

        for idx, s in enumerate(self.sources):
            if isinstance(s, BaseOp):
                exc_order.append(s.compile(arg_order))
                ops.append(idx)

        output = self.destination._uid if self.destination is not None else None

        iids = []
        for s in self.sources:
            if isinstance(s, BaseOp):
                pass
            else:
                iids.append(str(s._uid))


        def _op_compiled(*args):
            computed_values = [cmd(*args) for cmd, _, _ in exc_order]
            compartment_args = [args[arg_order.index(narg)] for narg in iids]
            _args = []
            for i in range(len(self.sources)):
                if i in ops:
                    _args.append(computed_values.pop(0))
                else:
                    _args.append(compartment_args.pop(0))

            return self.operation(*_args)


        return (_op_compiled, [str(output)], "op")

    def parse(self):
        assert self.is_compilable
        inputs = []
        for s in self.sources:
            if isinstance(s, BaseOp):
                needed_inputs, dest = s.parse()
                assert dest is None
                for inp in needed_inputs:
                    if inp not in inputs:
                        inputs.append(inp)
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

    def __repr__(self) -> str:
        return f"[OP:summation] {[self.source.name for source in self.sources]}"

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