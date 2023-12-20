from core.steps.step import Step


class Track(Step):
    def __init__(self, *args, compartment=None, store_value_function=None, **kwargs):
        super().__init__(*args, **kwargs)
        if compartment is None:
            raise RuntimeError("A track step requires a compartment to clamp to")
        if store_value_function is None:
            raise RuntimeError("A track step requires an function to pass the tacked value to")

        self.store = store_value_function
        self.compartment = compartment


    def __call__(self, *args, **kwargs):
        for component in self.components:
            self.store(self.components[component].compartments[self.compartment])


