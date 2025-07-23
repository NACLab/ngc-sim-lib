from .context import ContextObjectTypes

class ContextObjectDecorators:
    """
    This class contains all the decorators to automatically apply the correct
    "_type" field to the object. Beyond that they do not do anything.
    """
    @staticmethod
    def component(cls):
        cls._type = ContextObjectTypes.component
        return cls

    @staticmethod
    def process(cls):
        cls._type = ContextObjectTypes.process
        return cls

    # @staticmethod
    # def _operation(cls):
    #     cls._type = ContextObjectTypes.operation
    #     return cls



component = ContextObjectDecorators.component
process = ContextObjectDecorators.process
# operation = ContextObjectDecorators._operation
