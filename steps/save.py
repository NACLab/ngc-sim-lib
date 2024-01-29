from NGC_Learn_Core.steps.step import Step
import warnings

class Save(Step):
    def __init__(self, *args, directory_flag=None, **kwargs):
        super().__init__(*args, required_calls=['save'], **kwargs)
        if directory_flag is None:
            raise RuntimeError("A model step requires a \'directory_flag\' to bind to for construction")
        self.directory_flag = directory_flag

    def __call__(self, *args, **kwargs):
        directory = kwargs.get(self.directory_flag, None)

        if directory is None:
            warnings.warn("Save, " + str(self.directory_flag) + " is missing from keywords", stacklevel=6)
        else:
            for component in self.components:
                self.components[component].save(directory)


