from NGC_Learn_Core.steps.step import Step


class Evolve(Step):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_calls=['evolve'], **kwargs)

    def __call__(self, frozen=False, *args, **kwargs):
        if not frozen:
            for component in self.components:
                self.components[component].gather()
                self.components[component].evolve(**kwargs)


