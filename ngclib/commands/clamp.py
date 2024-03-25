from ngclib.commands.command import Command
import warnings

class Clamp(Command):
    """
    All components in ngclearn have compartments where they store information pertaining to their internal state that
    can be read into or out of by commands. The Clamp command is the primary way to manually set the value of a
    compartment on a set of components. The Clamp command requires a compartment that passed in value to be clamped to,
    as well as a clamp_name used to locate the value when called.
    """
    def __init__(self, components=None, compartment=None, clamp_name=None, **kwargs):
        """
        Required Calls on Components: ['clamp', 'name']

        :param components: a list of components to call clamp on
        :param compartment: the compartment being clamped to
        :param clamp_name: a keyword to bind the input for this command do
        """
        super().__init__(components=components, required_calls=['clamp'])
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

