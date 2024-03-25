from ngclib.commands import Command


class AdvanceState(Command):
    """
    As the general form of all models built in ngclearn are state machines this command is designed to advance the state
    of all components passed into the command. Prior to advancing the state of each component it will call the gather
    method of that component.
    """
    def __init__(self, components=None, **kwargs):
        """
        Required Calls on Components: ['advance_state', 'gather', 'name']
        :param components: The list of components to advance the state of
        """
        super().__init__(components=components, required_calls=['advance_state', 'gather'])

    def __call__(self, **kwargs):
        for component in self.components:
            self.components[component].gather()
            self.components[component].advance_state(**kwargs)
