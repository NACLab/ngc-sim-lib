from NGC_Learn_Core.commands import Command


class Evolve(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_calls=['evolve'])

    def __call__(self, frozen=False, *args, **kwargs):
        if not frozen:
            for component in self.components:
                self.components[component].gather()
                self.components[component].evolve(**kwargs)


