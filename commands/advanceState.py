from NGC_Learn_Core.commands import Command


class AdvanceState(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_calls=['advance_state', 'gather'])

    def __call__(self, **kwargs):
        for component in self.components:
            self.components[component].gather()
            self.components[component].advance_state(**kwargs)
