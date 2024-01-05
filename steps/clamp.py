from NGC_Learn_Core.steps.step import Step
import warnings

class Clamp(Step):
    def __init__(self, *args, compartment=None, clamp_name=None, **kwargs):
        super().__init__(*args, required_calls=['clamp'], **kwargs)
        if compartment is None:
            raise RuntimeError("A clamp step requires a \'compartment\' to clamp to for construction")
        if clamp_name is None:
            raise RuntimeError("A clamp step requires a \'clamp_name\' to bind to for construction")
        self.clamp_name = clamp_name
        self.compartment = compartment

    def __call__(self, *args, **kwargs):
        if self.clamp_name in kwargs.keys():
            for component in self.components:
                self.components[component].clamp(self.compartment, kwargs[self.clamp_name])
        else:
            warnings.warn("Clamp, " + str(self.clamp_name) + " is missing from cycle keywords", stacklevel=6)

