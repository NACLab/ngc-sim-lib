from abc import ABC, abstractmethod
from ngcsimlib.utils import check_attributes, get_current_context



class Command(ABC):
    """
    The base class for all commands found in ngcsimlib. At its core, a command is
    essentially a method to be called by the controller that affects the
    components in a simulated complex system / model in some way. When a command
    is made, a preprocessing step is run to verify that all of the needed
    attributes are present on each component. Note that this step does not
    ensure types or values, just that they do or do not exist.
    """

    """
    The Compile key is the name of the resolver the compile function will look for
    when compiling this command. If unset the compile will fail.
    """
    compile_key = None

    def __new__(cls, components=None, command_name=None, *args, **kwargs):
        if get_current_context() is not None:
            get_current_context().register_command(cls.__name__, *args, components=components, command_name=command_name, **kwargs)
        return super().__new__(cls)

    def __init__(self, components=None, command_name=None, required_calls=None):
        """
        Required calls on Components: ['name']

        Args:
            components: a list of components to run the command on

            required_calls: a list of required attributes for all components

            command_name: the name of the command on the controller
        """

        self.name = str(command_name)

        self.components = {}
        required_calls = ['name'] if required_calls is None else required_calls + ['name']
        for comp in components:
            if check_attributes(comp, required_calls, fatal=True):
                self.components[comp.name] = comp


        get_current_context().add_command(self)


    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

