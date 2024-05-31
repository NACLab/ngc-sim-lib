from .baseOp import BaseOp
class negate(BaseOp):
    """
    negates the first source compartment (other will be ignored) and overwrite the previous value
    """

    @staticmethod
    def operation(*sources):
        return -sources[0]