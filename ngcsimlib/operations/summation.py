from .baseOp import BaseOp

class summation(BaseOp):
    """
    Adds together all the provided compartment's values and overwrites the previous value
    """

    @staticmethod
    def operation(*sources):
        s = None
        for source in sources:
            if s is None:
                s = source
            else:
                s += source
        return s