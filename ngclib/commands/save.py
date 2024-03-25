from ngclib.commands import Command
import warnings

class Save(Command):
    """
    While training models there is a need to snapshot the model and save it to disk. The base controller in ngclib is
    able to save all the commands, components, connections, and steps to a file in order to rebuild the model. However,
    there is a good chance that the model will contain components that have parts to save beyond the parameters passed
    in to initialize the component. Ngclib solves this by providing a save command, this command will call a custom save
    method on all components provided to the command. This custom save method will be responsible for all custom values
    to be saved and where to save them inside of a provided directory.
    """
    def __init__(self, components=None, directory_flag=None, **kwargs):
        """
        Required Calls on Components: ['save', 'name']

        :param components: a list of components to call the save function on
        :param directory_flag: keyword for flag for the directory to save to
        """
        super().__init__(components=components, required_calls=['save'])
        if directory_flag is None:
            raise RuntimeError("A model step requires a \'directory_flag\' to bind to for construction")
        self.directory_flag = directory_flag

    def __call__(self, *args, **kwargs):
        if self.directory_flag in kwargs.keys():
            val = kwargs.get(self.directory_flag, None)
        elif len(args) > 0:
            val = args[0]
        else:
            val = None


        if val is None:
            warnings.warn("Save, " + str(self.directory_flag) + " is missing from keyword arguments and no "
                                                                "positional arguments were provided", stacklevel=6)
        else:
            for component in self.components:
                self.components[component].save(val)


