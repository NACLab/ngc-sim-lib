from abc import ABC, abstractmethod
from ngclib.utils import check_attributes


class Command(ABC):
    """
    The base class for all commands found in ngclib. At its core all a command is, is a method to be called by the
    controller that affects components in the model in some way. When a command is made a preprocessing step is run to
    verify that all the needed attributes are present on each component. This does not ensure types or values, just that
    they do or do not exist.
    """
    def __init__(self, components=None, required_calls=None):
        """
        Required Calls on Components: ['name']

        :param components: A list of components to run the command on
        :param required_calls: a list of required attributes for all components
        """
        self.components = {}
        required_calls = ['name'] if required_calls is None else required_calls + ['name']
        for comp in components:
            if check_attributes(comp, required_calls, fatal=True):
                self.components[comp.name] = comp

    @abstractmethod
    def __call__(self, **kwargs):
        pass
