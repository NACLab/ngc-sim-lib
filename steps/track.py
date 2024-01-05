from NGC_Learn_Core.steps.step import Step
import warnings

class Track(Step):
    def __init__(self, *args, compartment=None, tracker=None, **kwargs):
        super().__init__(*args, **kwargs)
        if compartment is None:
            raise RuntimeError("A track step requires a \'compartment\' to clamp to for construction")
        if tracker is None:
            raise RuntimeError("A track step requires a \'tracker\' to bind to for construction")

        self.tracker = tracker
        self.compartment = compartment


    def __call__(self, *args, **kwargs):
        if self.tracker in kwargs.keys():
            for component in self.components:
                kwargs[self.tracker].append(self.components[component].compartments[self.compartment])
        else:
            warnings.warn("Tracker, " + str(self.tracker) + " is missing from cycle keywords", stacklevel=6)

