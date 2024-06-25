from ngcsimlib.compartment import Compartment
from ngcsimlib.utils import get_current_context
from ngcsimlib.utils.help import Guides
from ngcsimlib.logger import debug


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
        cc = get_current_context()
        if cc is None:
            self.path = "/" + name
        else:
            self.path = cc.path + "/" + name
            cc.register_component(self, name, *args, **kwargs)
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
        if get_current_context() is not None:
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

    @staticmethod
    def _format_defaults(cls, params):

        args_count = cls._orig_init.__code__.co_argcount
        defaults = cls._orig_init.__defaults__
        kwargs = cls._orig_init.__code__.co_varnames[:args_count]
        if defaults is not None:
            for i, j in zip(kwargs[-len(defaults):], defaults):
                if i in params.keys():
                    params[i] = params[i] + f" (default: {j})"

        for key in kwargs[1:]:
            if key not in params.keys() and key != "name":
                debug(f"{key} is missing from {cls.__name__}'s help method")

    def __new__(cls, *clargs, **clkwargs):
        """
        Wraps the class adding a pre/post-init method and some additional methods
        """
        x = super().__new__(cls, *clargs, **clkwargs)

        x._orig_init = x.__init__

        def wrapped_init(self, *args, **kwargs):
            if self.__dict__.get("_meta_init", False):
                x._orig_init(self, *args, **kwargs)
            else:
                cls.pre_init(self, *args, **kwargs)
                x._orig_init(self, *args, **kwargs)
                cls.post_init(self, *args, **kwargs)

        x.__init__ = wrapped_init

        x.add_connection = cls.add_connection
        x.gather = cls.gather

        if hasattr(x, "help"):
            _orig_help = x.help
            def _wrapped_help(*args):
                info = _orig_help()
                if info is not None:
                    if "hyperparameters" in info.keys():
                        x._format_defaults(x, info["hyperparameters"])

                return info
            x.help = _wrapped_help

        x.guides = Guides(x)

        return x
