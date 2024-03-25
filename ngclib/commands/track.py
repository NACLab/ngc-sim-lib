from ngclib.commands import Command
import warnings

class Track(Command):
    """
    While running a model there is a need to track a compartment value over time, usually for visualization. To do this
    ngclib provides a track command. This command stores the values of a compartment from a set of components into a
    provided object. This provided object is expected to have a `.append` method implemented. Each element appended to
    this object will be values of the compartment for each provided component, in the same order they were provided in.
    """
    def __init__(self, components=None, compartment=None, tracker=None, **kwargs):
        """
        Required Calls on Components: ['name']

        :param components: a list of components to track values from
        :param compartment: the compartment to extract information from
        :param tracker: the keyword for which the tracking object will be passed in by
        """
        super().__init__(components=components)
        if compartment is None:
            raise RuntimeError("A track command requires a \'compartment\' to clamp to for construction")
        if tracker is None:
            raise RuntimeError("A track command requires a \'tracker\' to bind to for construction")

        self.tracker = tracker
        self.compartment = compartment


    def __call__(self, *args, **kwargs):
        if self.tracker in kwargs.keys():
            val = kwargs.get(self.tracker, None)
        elif len(args) > 0:
            val = args[0]
        else:
            val = None

        if val is None:
            warnings.warn("Tracker, " + str(self.tracker) + " is missing from keyword arguments and no "
                                                            "positional arguments were provided", stacklevel=6)
        else:
            vals = []
            for component in self.components:
                vals.append(self.components[component].compartments[self.compartment])

            val.append(vals)

