from NGC_Learn_Core.commands import Command
import warnings

class Save(Command):
    def __init__(self, *args, directory_flag=None, **kwargs):
        super().__init__(*args, required_calls=['save'])
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


