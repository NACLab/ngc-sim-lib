from ngcsimlib.utils import make_unique_path, check_attributes, check_serializable, load_from_path
from ngcsimlib.logger import warn, info
from ngcsimlib.utils import get_compartment_by_name, \
    get_context, add_context, get_current_path, get_current_context, set_new_context
from ngcsimlib.compilers.command_compiler import dynamic_compile
import json, os


class Context:
    def __new__(cls, name, *args, **kwargs):
        assert len(name) > 0
        con = get_context(str(name))
        if con is None:
            return super().__new__(cls)
        else:
            return con

    def __init__(self, name):
        if hasattr(self, "_init"):
            return
        self._init = True

        add_context(str(name), self)
        self.components = {}
        self._component_paths = {}
        self.commands = {}
        self.name = name

        # Used for contexts
        self.path = get_current_path() + "/" + str(name)
        self._last_context = ""

        self._json_objects = {"ops": [], "components": {}, "commands": {}}

    def __enter__(self):
        self._last_context = get_current_path()
        set_new_context(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_new_context(self._last_context)

    def get_components(self, *args):
        _components = []
        for a in args:
            if a in self.components.keys():
                _components.append(self.components[a])
        return _components

    def register_op(self, op):
        self._json_objects['ops'].append(op.dump())

    def register_command(self, klass, *args, components=None, command_name=None, **kwargs):
        _components = [components.name for components in components]
        self._json_objects['commands'][command_name] = {"class": klass, "components": _components, "args": args,
                                                        "kwargs": kwargs}

    def register_component(self, component, *args, **kwargs):
        if component.path in self._component_paths.keys():
            return
        self._component_paths[component.path] = component

        c_path = component.path
        c_class = component.__class__.__name__

        _args = []

        for a in args:
            try:
                json.dumps([a])
                _args.append(a)
            except:
                info("Failed to serialize \"", a, "\" in ", component.path, sep="")

        _kwargs = {key: value for key, value in kwargs.items()}
        bad_keys = check_serializable(_kwargs)
        for key in bad_keys:
            del _kwargs[key]
            info("Failed to serialize \"", key, "\" in ", component.path, sep="")

        obj = {"class": c_class, "args": _args, "kwargs": _kwargs}
        self._json_objects['components'][c_path] = obj

    def add_component(self, component):
        if component.name not in self.components.keys():
            self.components[component.name] = component

    def add_command(self, command, name=None):
        name = command.name if name is None else name

        self.commands[name] = command
        self.__setattr__(name, command)

    def save_to_json(self, directory, model_name=None, custom_save=True):
        """
        Dumps all the required json files to rebuild the current controller to a specified directory. If there is a
        `save` command present on the controller and custom_save is True, it will run that command as well.

        Args:
            directory: The top level directory to save the model to

            model_name: The name of the model, if None or if there is already a
                model with that name a uid will be used or appended to the name
                respectively. (Default: None)

            custom_save: A boolean that if true will attempt to call the `save`
                command if present on the controller (Default: True)

        Returns:
            a tuple where the first value is the path to the model, and the
                second is the path to the custom save folder if custom_save is
                true and None if false
        """
        path = make_unique_path(directory, model_name)

        with open(path + "/ops.json", 'w') as fp:
            json.dump(self._json_objects['ops'], fp, indent=4)

        with open(path + "/commands.json", 'w') as fp:
            json.dump(self._json_objects['commands'], fp, indent=4)

        with open(path + "/components.json", 'w') as fp:
            hyperparameters = {}

            for c_path, component in self._json_objects['components'].items():
                if component['kwargs'].get('parameter_map', None) is not None:
                    for cKey, pKey in component['kwargs']['parameter_map'].items():
                        pVal = component['kwargs'][cKey]
                        if pKey not in hyperparameters.keys():
                            hyperparameters[pKey] = []
                        hyperparameters[pKey].append((c_path, cKey, pVal))

            hp = {}
            for param in hyperparameters.keys():
                matched = True
                hp[param] = None
                for _, _, pVal in hyperparameters[param]:
                    if hp[param] is None:
                        hp[param] = pVal
                    elif hp[param] != pVal:
                        del hp[param]
                        matched = False
                        break

                for c_path, cKey, _ in hyperparameters[param]:
                    if matched:
                        self._json_objects['components'][c_path]['kwargs'][cKey] = param

                    else:
                        warn("Unable to extract hyperparameter", param,
                             "as it is mismatched between components. Parameter will not be extracted")

            for c_path, component in self._json_objects['components'].items():
                if "parameter_map" in component['kwargs'].keys():
                    del component['kwargs']["parameter_map"]

            obj = {"components": self._json_objects['components']}
            if len(hp.keys()) != 0:
                obj["hyperparameters"] = hp

            json.dump(obj, fp, indent=4)

        if custom_save:
            os.mkdir(path + "/custom")
            if check_attributes(self, ['save']):
                self.save(path + "/custom")
            else:
                warn("Context doesn't have a save command registered. Saving all components")
                for component in self.components.values():
                    if check_attributes(component, ['save']):
                        component.save(path + "/custom")

        return (path, path + "/custom") if custom_save else (path, None)

    def load_from_dir(self, directory, custom_folder="/custom"):
        """
        Builds a controller from a directory. Designed to be used with
        `save_to_json`.

        Args:
            directory: the path to the model

            custom_folder: The name of the custom data folder for building
                components. (Default: `/custom`)
        """
        self.make_components(directory + "/components.json", directory + custom_folder)
        self.make_ops(directory + "/ops.json")
        self.make_commands(directory + "/commands.json")

    def make_components(self, path_to_components_file, custom_file_dir=None):
        """
        Loads a collection of components from a json file. Follow
        `components.schema` for the specific format of the json file.

        Args:
            path_to_components_file: the path to the file, including the name
                and extension

            custom_file_dir: the path to the custom directory for custom load methods,
                this directory is named `custom` if the save_to_json method is
                used. (Default: None)
        """
        with open(path_to_components_file, 'r') as file:
            componentsConfig = json.load(file)

            parameterMap = {}
            components = componentsConfig["components"]
            if "hyperparameters" in componentsConfig.keys():
                for c_path, component in components.items():
                    for pKey, pValue in componentsConfig["hyperparameters"].items():
                        for cKey, cValue in component['kwargs'].items():
                            if pKey == cValue:
                                component['kwargs'][cKey] = pValue
                                parameterMap[cKey] = pKey

            for c_path, component in components.items():
                klass = load_from_path(component["class"])
                _args = component['args']
                _kwargs = component['kwargs']
                obj = klass(*_args, **_kwargs, parameter_map=parameterMap)

                if check_attributes(obj, ["load"]):
                    obj.load(custom_file_dir)

    def make_ops(self, path_to_ops_file):
        """
        Loads a collection of ops from a json file. Follow `ops.schema`
        for the specific format of this json file.

        Args:
            path_to_ops_file: the path of the file, including the name
                and extension
        """
        with open(path_to_ops_file, 'r') as file:
            ops = json.load(file)
            for op in ops:
                self._make_op(op)

    def make_commands(self, path_to_commands_file):
        with open(path_to_commands_file, 'r') as file:
            commands = json.load(file)
            for c_name, command in commands.items():
                if command['class'] == "dynamic_compiled":
                    self.compile_command_key(
                        *self.get_components(*command['components']), compile_key=command['compile_key'], name=c_name)
                else:
                    klass = load_from_path(command['class'])
                    klass(*command['args'], **command['kwargs'], components=self.get_components(*command['components']),
                          command_name=c_name)

    def _make_op(self, op_spec):
        klass = load_from_path(op_spec["class"])
        _sources = []
        for s in op_spec["sources"]:
            if isinstance(s, dict):
                _sources.append(self._make_op(s))
            else:
                _sources.append(get_compartment_by_name(get_current_context(), s))

        obj = klass(*_sources)

        if op_spec['destination'] is None:
            return obj

        else:
            dest = get_compartment_by_name(get_current_context(), op_spec['destination'])
            dest << obj

    @staticmethod
    def dynamicCommand(fn):
        if get_current_context() is not None:
            get_current_context().__setattr__(fn.__name__, fn)
        return fn

    def compile_command_key(self, *components, compile_key, name=None):
        cmd, args = dynamic_compile(*components, compile_key=compile_key)
        if name is None:
            name = compile_key

        klass = "dynamic_compiled"
        _components = [components.name for components in components]
        self._json_objects['commands'][name] = {"class": klass, "components": _components, "compile_key": compile_key}
        self.__setattr__(name, cmd)
        return cmd, args
