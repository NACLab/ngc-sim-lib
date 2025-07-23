from ngcsimlib._src.operations.BaseOp import BaseOp
import ast


class Summation(BaseOp):
    """
    The summation operation. This operation takes in any number of compartments
    and sums them together before passing the value off to the destination
    compartment.
    """
    def __init__(self, *compartments):
        super().__init__(*compartments)
        self.astOp = ast.Add()

    def _get_value(self):
        return sum(self._comps)


