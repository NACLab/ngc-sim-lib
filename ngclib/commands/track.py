from ngclib.commands import Command
from ngclib.utils import extract_args
import warnings

class Track(Command):
    """
    While running a model there is a need to track a compartment value over time, usually for visualization. To do this
    ngclib provides a track command. This command stores the values of a compartment from a set of components into a
    provided object. This provided object is expected to have a `.append` method implemented. Each element appended to
    this object will be values of the compartment for each provided component, in the same order they were provided in.
    """
    def __init__(self, components=None, compartment=None, tracker=None,
                 command_name=None, **kwargs):
        """
        Required Calls on Components: ['name']

        :param components: a list of components to track values from
        :param compartment: the compartment to extract information from
        :param tracker: the keyword for which the tracking object will be passed in by
        :param command_name: the name of the command on the controller
        """
        super().__init__(components=components)
        if compartment is None:
            raise RuntimeError(self.name + " requires a \'compartment\' to clamp to for construction")
        if tracker is None:
            raise RuntimeError(self.name + " requires a \'tracker\' to bind to for construction")

        self.tracker = tracker
        self.compartment = compartment


    def __call__(self, *args, **kwargs):
        try:
            vals = extract_args([self.tracker], *args, **kwargs)
        except RuntimeError:
            warnings.warn(self.name + ", " + str(self.tracker) + " is missing from keyword arguments and no "
                                                                "positional arguments were provided", stacklevel=6)
            return

        v = []
        for component in self.components:
            v.append(self.components[component].compartments[self.compartment])
        vals[self.tracker].append(v)

