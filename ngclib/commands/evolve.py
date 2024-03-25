from ngclib.commands import Command


class Evolve(Command):
    """
    In many models there is a need to have either a backward pass or a separate method to update some internal state. In
    general this can be mapped to evolve. Like with advanceState this will call the gather method prior to calling the
    evolve function of every component.

    """
    def __init__(self, components=None, frozen_flag=None, **kwargs):
        """
        Required Calls on Components: ['evolve', 'gather', 'name']
        :param components: The list of components to evolve
        :param frozen_flag: the keyword for the flag to freeze this evolve step
        """
        super().__init__(components=components, required_calls=['evolve'])

        self.frozen_flag = frozen_flag

    def __call__(self, *args, **kwargs):
        if self.frozen_flag in kwargs.keys():
            val = kwargs.get(self.frozen_flag, None)
        elif len(args) > 0:
            val = args[0]
        else:
            val = False

        if not val:
            for component in self.components:
                self.components[component].gather()
                self.components[component].evolve(**kwargs)


