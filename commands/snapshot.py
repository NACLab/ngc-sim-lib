from ngclib.commands import Command
from ngclib.utils import check_attributes
import warnings

class Snapshot(Command):
    def __init__(self, components=None, attribute=None, **kwargs):
        super().__init__(components=components, required_calls=[attribute])
        self.attribute = attribute


    def __call__(self, *args, **kwargs):
        vals = []
        for component in self.components:
            vals.append(getattr(self.components[component], self.attribute))

        return vals if len(vals) > 1 else vals[0]



