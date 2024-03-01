from NGC_Learn_Core.commands import Command
import warnings

class Track(Command):
    def __init__(self, components=None, compartment=None, tracker=None, **kwargs):
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
            for component in self.components:
                val.append(self.components[component].compartments[self.compartment])


