from ngclib.commands.command import Command
from ngclib.utils import extract_args

class Clamp(Command):
    """
    All components in ngclearn have compartments where they store information
    pertaining to their internal state that can be read into or out of by
    commands. The Clamp command is the primary way to manually set the value of
    a compartment on a set of components. The Clamp command requires a
    compartment that a value can passed into and be clamped to,
    as well as a `clamp_name` used to locate the value when called.
    """
    def __init__(self, components=None, compartment=None, clamp_name=None, **kwargs):
        """
        Required calls on Components: ['clamp', 'name']

        Args:
            components: a list of components to call clamp on

            compartment: the compartment being clamped to

            clamp_name: a keyword to bind the input for this command do
        """
        super().__init__(components=components, required_calls=['clamp'])
        if compartment is None:
            raise RuntimeError("A clamp command requires a \'compartment\' to clamp to for construction")
        if clamp_name is None:
            raise RuntimeError("A clamp command requires a \'clamp_name\' to bind to for construction")

        self.clamp_name = clamp_name
        self.compartment = compartment

    def __call__(self, *args, **kwargs):
        try:
            vals = extract_args([self.clamp_name], *args, **kwargs)
        except RuntimeError:
            raise RuntimeError("Clamp, " + str(self.clamp_name) + " is missing from keyword arguments or a positional "
                                                                  "arguments can be provided")

        for component in self.components:
            self.components[component].clamp(self.compartment, vals[self.clamp_name])
