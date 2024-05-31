from .baseOp import BaseOp
class overwrite(BaseOp):
    """
    The default operation behavior for cable's
    Overwrites the previous value with the first source value (all other sources will be ignored)
    """
    @staticmethod
    def operation(*sources):
        return sources[0]
