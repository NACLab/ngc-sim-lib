from ngcsimlib.compartment import Compartment
from ngcsimlib.utils import get_current_context


class MetaComponent(type):
    """
    This is the metaclass for the component objects in ngc-learn. This does a large amount of setup work behind the
    scenes to link everything together in the context that it is constructed in. In addition to this it also is
    responsible for adding all compartment value to the global hashmap.
    """

    @staticmethod
    def pre_init(self, name, *args, **kwargs):
        """
        Called before the classes default init
        """
        self.connections = []
        self.path = get_current_context().path + "/" + name
        get_current_context().register_component(self, name, *args, **kwargs)
        self._meta_init = True


    @staticmethod
    def post_init(self, *args, **kwargs):
        """
        Called after the classes default init
        """
        for key, value in self.__dict__.items():
            if Compartment.is_compartment(value):
                value._setup(self, key)
        # add component to context
        get_current_context().add_component(self)

    @staticmethod
    def add_connection(self, op):
        """
        A needed function by compartments to be able to add incoming connections to their parent component
        """
        self.connections.append(op)
        get_current_context().register_op(op)

    @staticmethod
    def gather(self):
        """
        Runs all the connections for the given component to collect values for its own compartments
        """
        for comm in self.connections:
            comm()

    def __new__(cls, *clargs, **clkwargs):
        """
        Wraps the class adding a pre/post-init method and some additional methods
        """
        x = super().__new__(cls, *clargs, **clkwargs)

        orig_init = x.__init__

        def wrapped_init(self, *args, **kwargs):
            if self.__dict__.get("_meta_init", False):
                orig_init(self, *args, **kwargs)
            else:
                cls.pre_init(self, *args, **kwargs)
                orig_init(self, *args, **kwargs)
                cls.post_init(self, *args, **kwargs)

        x.__init__ = wrapped_init
        x.add_connection = cls.add_connection
        x.gather = cls.gather
        return x
