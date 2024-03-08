from ngclib.commands import Command
from ngclib.utils import check_attributes
import warnings

class Compound(Command):
    def __init__(self, components=None, command_name=None, command_list=None, controller=None, **kwargs):
        super().__init__(components=components)
        if controller is None:
            raise RuntimeError("The controller is needed to build a compound command (This should be passed in by default)")
        if command_list is None or len(command_list) == 0:
            warnings.warn("The command list for command " + command_name + " is None or empty")

        self.command_list = command_list
        self.controller = controller

        check_attributes(self.controller, self.command_list, fatal=True)

    def __call__(self, *args, **kwargs):
        for command in self.command_list:
            self.controller.runCommand(command, *args, **kwargs)


