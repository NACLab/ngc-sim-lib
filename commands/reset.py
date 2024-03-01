from NGC_Learn_Core.commands import Command
import warnings

class Reset(Command):
    def __init__(self, components=None, reset_name=None, **kwargs):
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
