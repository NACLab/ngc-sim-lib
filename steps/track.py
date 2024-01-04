from steps.step import Step


class Track(Step):
    def __init__(self, *args, compartment=None, tracker=None, **kwargs):
        super().__init__(*args, **kwargs)
        if compartment is None:
            raise RuntimeError("A track step requires a compartment to clamp to")

        self.store_name = tracker
        self.compartment = compartment


    def __call__(self, *args, **kwargs):
        if self.store_name in kwargs.keys():
            for component in self.components:
                kwargs[self.store_name].append(self.components[component].compartments[self.compartment])


