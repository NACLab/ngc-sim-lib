from steps.step import Step


class Clamp(Step):
    def __init__(self, *args, compartment=None, clamp_name=None, **kwargs):
        super().__init__(*args, required_calls=['clamp'], **kwargs)
        if compartment is None:
            raise RuntimeError("A clamp step requires a compartment to clamp to")
        self.clamp_name = clamp_name
        self.compartment = compartment

    def __call__(self, *args, **kwargs):
        if self.clamp_name in kwargs.keys():
            for component in self.components:
                self.components[component].clamp(self.compartment, kwargs[self.clamp_name])


