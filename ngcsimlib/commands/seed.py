from ngcsimlib.commands.command import Command
from ngcsimlib.utils import extract_args
from ngcsimlib.logger import error

class Seed(Command):
    """
    In many models there is a need to seed the randomness of a model. While many
    components will take seeds in at construction these are not always serializable
    or there might be a need to reseed the model after initialization. To solve
    this problem ngcsimlib offers the Seed command. This command will simply go
    through all the provided components and call see with the specified value.
    """

    def __init__(self, components=None, seed_name=None,
                 command_name=None, **kwargs):
        """
        Required calls on Components: ['seed', 'name']

        Args:
            components: a list of components to call seed on

            seed_name: a keyword to bind the input for this command do

            command_name: the name of the command on the controller

        """
        super().__init__(components=components, command_name=command_name,
                         required_calls=['seed'])
        if seed_name is None:
            error(self.name, "requires a \'seed_name\' to bind to for construction")

        self.seed_name = seed_name

    def __call__(self, *args, **kwargs):
        try:
            vals = extract_args([self.seed_name], *args, **kwargs)
        except RuntimeError:
            error(self.name, ",", self.seed_name,
                  "is missing from keyword arguments or a positional arguments can be provided")

        for component in self.components:
            self.components[component].seed(vals[self.seed_name])

