from ngcsimlib.compartment import Compartment
class MetaComponent(type):
    @staticmethod
    def super_init(self, *args, **kwargs):
        self.connections = []

    @staticmethod
    def post_init(self, *args, **kwargs):
        for key, value in self.__dict__.items():
            if Compartment.is_compartment(value):
                value._setup(self.add_connection)

    @staticmethod
    def add_connection(self, op):
        print(f"[MetaComponent/add_connection] added: {op}, self.connnections: {self.connections}")
        self.connections.append(op)

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


