from NGC_Learn_Core.steps.step import Step
import warnings

class Reset(Step):
    def __init__(self, *args, reset_name=None, **kwargs):
        super().__init__(*args, required_calls=['reset'], **kwargs)
        if reset_name is None:
            raise RuntimeError("A reset step must have a reset_name")
        self.reset_name = reset_name

    def __call__(self, *args, **kwargs):
        should_reset = kwargs.get(self.reset_name, False)
        if should_reset:
            for component in self.components:
                self.components[component].reset()
        else:
            warnings.warn("Reset, " + str(self.reset_name) + " is missing from cycle keywords", stacklevel=6)


