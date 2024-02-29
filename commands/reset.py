from NGC_Learn_Core.commands import Command
import warnings

class Reset(Command):
    def __init__(self, *args, reset_name=None, **kwargs):
        super().__init__(*args, required_calls=['reset'])
        if reset_name is None:
            raise RuntimeError("A reset command requires a \'reset_name\' to bind to for construction")
        self.reset_name = reset_name

    def __call__(self, *args, **kwargs):
        if self.reset_name in kwargs.keys():
            flag_val = kwargs.get(self.reset_name, None)
        elif len(args) > 0:
            flag_val = args[0]
        else:
            flag_val = None

        if flag_val: # flag should be True to trigger this
            for component in self.components:
                self.components[component].reset()

        elif flag_val is None:
            warnings.warn("Reset, " + str(self.reset_name) + " is missing from keyword arguments and no "
                                                             "positional arguments were provided", stacklevel=6)
