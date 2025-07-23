from ngcsimlib._src.operations.BaseOp import BaseOp
import ast


class Product(BaseOp):
    """
    The product operation. This operation takes in any number of compartments
    and multiplies them together before passing the value off to the destination
    compartment.
    """
    def __init__(self, *compartments):
        super().__init__(*compartments)
        self.astOp = ast.Mult()

    def _get_value(self):
        x = 1
        for comp in self._comps:
            x *= comp.get()
        return x


