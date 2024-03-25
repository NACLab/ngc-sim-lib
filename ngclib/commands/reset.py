from ngclib.commands import Command
import warnings

class Reset(Command):
    """
    In every model there is a need to reset it back to some intial state. As such many components that maintain a state
    have a reset method implemented on them. The reset command will go through the list of components and reset them
    each of them.
    """
    def __init__(self, components=None, reset_name=None, **kwargs):
        """
        Required Calls on Components: ['reset', 'name']

        :param components: a list of components to reset
        :param reset_name: the keyword for the flag on if the reset should happen
        """
        super().__init__(components=components, required_calls=['reset'])
        if reset_name is None:
            raise RuntimeError("A reset command requires a \'reset_name\' to bind to for construction")
        self.reset_name = reset_name

    def __call__(self, *args, **kwargs):
        if self.reset_name in kwargs.keys():
            val = kwargs.get(self.reset_name, None)
        elif len(args) > 0:
            val = args[0]
        else:
            val = None

        if val:
            for component in self.components:
                self.components[component].reset()

        elif val is None:
            warnings.warn("Reset, " + str(self.reset_name) + " is missing from keyword arguments and no "
                                                             "positional arguments were provided", stacklevel=6)
