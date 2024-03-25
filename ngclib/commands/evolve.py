from ngclib.commands import Command
from ngclib.utils import extract_args

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
        vals = {}
        try:
            vals = extract_args([self.frozen_flag], *args, **kwargs)
        except RuntimeError:
            vals[self.frozen_flag] = False

        if not vals[self.frozen_flag]:
            for component in self.components:
                self.components[component].gather()
                self.components[component].evolve(**kwargs)


