from ngcsimlib.compartment import Compartment
from ngcsimlib.utils import get_current_context


class MetaComponent(type):
    @staticmethod
    def super_init(self, name, *args, **kwargs):
        self.connections = []
        self.path = get_current_context().path + "/" + name
        get_current_context().register_component(self, name, *args, **kwargs)

    @staticmethod
    def post_init(self, *args, **kwargs):
        for key, value in self.__dict__.items():
            if Compartment.is_compartment(value):
                value._setup(self, key)
        # add component to context
        get_current_context().add_component(self)

    @staticmethod
    def add_connection(self, op):
        self.connections.append(op)
        get_current_context().register_op(op)

    @staticmethod
    def gather(self):
        for comm in self.connections:
            comm()

    def __new__(cls, *clargs, **clkwargs):
        x = super().__new__(cls, *clargs, **clkwargs)

        orig_init = x.__init__

        def wrapped_init(self, *args, **kwargs):
            cls.super_init(self, *args, **kwargs)
            orig_init(self, *args, **kwargs)
            cls.post_init(self, *args, **kwargs)

        x.__init__ = wrapped_init
        x.add_connection = cls.add_connection
        x.gather = cls.gather
        return x
