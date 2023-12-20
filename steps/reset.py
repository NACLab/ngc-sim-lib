from core.steps.step import Step


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


