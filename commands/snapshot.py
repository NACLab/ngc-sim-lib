from NGC_Learn_Core.commands import Command
from NGC_Learn_Core.utils import check_attributes
import warnings

class Snapshot(Command):
    def __init__(self, *args, attribute=None, **kwargs):
        super().__init__(*args)

        for component in self.components:
            check_attributes(self.components[component], [attribute], fatal=True)

        self.attribute = attribute


    def __call__(self, *args, **kwargs):
        vals = []
        for component in self.components:
            vals.append(getattr(self.components[component], self.attribute))
        return vals


