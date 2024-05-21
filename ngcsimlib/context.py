class Context:
    _current_context = ""
    _contexts = {"": None}

    @classmethod
    def get_current_context(cls):
        return Context._contexts[Context._current_context]

    def __new__(cls, name, *args, **kwargs):
        assert len(name) > 0

        if Context._current_context + "/" + str(name) in Context._contexts.keys():
            return Context._contexts[Context._current_context + "/" + str(name)]
        return super().__new__(cls)

    def __init__(self, name):
        if hasattr(self, "_init"):
            return
        self._init = True

        Context._contexts[Context._current_context + "/" + str(name)] = self
        self.components = {}
        self.commands = {}
        self.name = name

        #Used for contexts
        self.path = Context._current_context + "/" + str(name)
        self._last_context = ""



    def __enter__(self):
        self._last_context = Context._current_context
        Context._current_context = self.path
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Context._current_context = self._last_context

    def register_connection(self, *args):
        print("Registering", *args)

    def add_component(self, component):
        self.components[component.name] = component

    def build_component(self, component_type, *args, **kwargs):
        print("building component:", component_type, "\tusing", args, kwargs)


    def add_command(self, command):
        self.commands[command.name] = command
        self.__setattr__(command.name, command)


    @staticmethod
    def dynamicCommand(fn):
        if Context.get_current_context() is not None:
            Context.get_current_context().__setattr__(fn.__name__, fn)
        return fn