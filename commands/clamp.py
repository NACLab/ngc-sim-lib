from NGC_Learn_Core.commands.command import Command
import warnings

class Clamp(Command):
    def __init__(self, *args, compartment=None, clamp_name=None):
        super().__init__(*args, required_calls=['clamp'])
        if compartment is None:
            raise RuntimeError("A clamp command requires a \'compartment\' to clamp to for construction")
        if clamp_name is None:
            raise RuntimeError("A clamp command requires a \'clamp_name\' to bind to for construction")

        self.clamp_name = clamp_name
        self.compartment = compartment

    def __call__(self, *args, **kwargs):
        if self.clamp_name in kwargs.keys():
            val = kwargs.get(self.clamp_name, None)
        elif len(args) > 0:
            val = args[0]
        else:
            raise RuntimeError("Clamp, " + str(self.clamp_name) + " is missing from keyword arguments or a positional "
                                                                  "arguments can be provided")

        for component in self.components:
            self.components[component].clamp(self.compartment, val)

