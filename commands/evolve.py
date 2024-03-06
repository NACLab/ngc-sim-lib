from ngclib.commands import Command


class Evolve(Command):
    def __init__(self, components=None, **kwargs):
        super().__init__(components=components, required_calls=['evolve'])

    def __call__(self, frozen=False, *args, **kwargs):
        if not frozen:
            for component in self.components:
                self.components[component].gather()
                self.components[component].evolve(**kwargs)


