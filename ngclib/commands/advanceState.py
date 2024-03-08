from ngclib.commands import Command


class AdvanceState(Command):
    def __init__(self, components=None, **kwargs):
        super().__init__(components=components, required_calls=['advance_state', 'gather'])

    def __call__(self, **kwargs):
        for component in self.components:
            self.components[component].gather()
            self.components[component].advance_state(**kwargs)
