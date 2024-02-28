from NGC_Learn_Core.utils import load_attribute, check_attributes, load_from_path
import json, uuid, os


class Controller:
    def __init__(self):
        self.steps = []
        self.commands = {}
        self.components = {}
        self.connections = []

        self._json_objects = {
            "commands": [],
            "steps": [],
            "components": [],
            "connections": []
        }

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def runCycle(self, **kwargs):
        for step in self.steps:
            self[step](**kwargs)

    def verify_cycle(self):
        for component in self.components.keys():
            self.components[component].verify_connections()

    def connect(self, source_component, source_compartment, target_component, target_compartment, bundle=None):
        self.components[target_component].create_incoming_connection(
            self.components[source_component].create_outgoing_connection(source_compartment), target_compartment,
            bundle)
        self.connections.append((source_component, source_compartment, target_component, target_compartment, bundle))
        self._json_objects['connections'].append({
            "source_component": source_component,
            "source_compartment": source_compartment,
            "target_component": target_component,
            "target_compartment": target_compartment,
            "bundle": bundle})

    def make_connections(self, path_to_cables_file):
        with open(path_to_cables_file, 'r') as file:
            cables = json.load(file)
            for cable in cables:
                self.connect(**cable)

    def make_components(self, path_to_components_file, custom_file_dir=None):
        with open(path_to_components_file, 'r') as file:
            components = json.load(file)
            for component in components:
                self.add_component(**component, directory=custom_file_dir)

    def make_steps(self, path_to_steps_file):
        with open(path_to_steps_file, 'r') as file:
            steps = json.load(file)
            for step in steps:
                self.add_step(**step)

    def make_commands(self, path_to_commands_file):
        with open(path_to_commands_file, 'r') as file:
            commands = json.load(file)
            for command in commands:
                self.add_command(**command)

    def add_step(self, command_name):
        if command_name not in self.commands.keys():
            raise RuntimeError(str(command_name) + " is not a registered command")
        self.steps.append(command_name)
        self._json_objects['steps'].append({"command_name": command_name})

    def add_component(self, component_type, match_case=False, absolute_path=False, **kwargs):
        Component_class = load_from_path(path=component_type, match_case=match_case, absolute_path=absolute_path)
        count = Component_class.__init__.__code__.co_argcount - 1
        named_args = Component_class.__init__.__code__.co_varnames[1:count]
        try:
            component = Component_class(**kwargs)
        except TypeError as E:
            print(E)
            raise RuntimeError(str(E) + "\nProvided keyword arguments:\t" + str(list(kwargs.keys())) +
                               "\nRequired keyword arguments:\t" + str(list(named_args)))

        check_attributes(component, ["name", "verify_connections"], fatal=True)
        self.components[component.name] = component

        self._json_objects['components'].append({"component_type": component_type,
                                                 "match_case": match_case,
                                                 "absolute_path": absolute_path,
                                                 } | kwargs)

        return component

    def add_command(self, command_type, command_name, match_case=False, absolute_path=False, components=None,
                    **kwargs):
        Command_class = load_from_path(path=command_type, match_case=match_case, absolute_path=absolute_path)
        if not callable(Command_class):
            raise RuntimeError("The object named \"" + Command_class.__name__ + "\" is not callable. Please make sure "
                                                                                "the object is callable and returns a "
                                                                                  "callable object")
        componentObjs = None
        if components is not None:
            componentObjs = [self.components[name] for name in components]

        command = Command_class(*componentObjs, **kwargs)
        self.commands[command_name] = command
        self.__setattr__(command_name, command)
        self._json_objects['commands'].append({"command_type": command_type,
                                            "command_name": command_name,
                                            "match_case": match_case,
                                            "absolute_path": absolute_path,
                                            "components": components,
                                            } | kwargs)
        return command

    def runCommand(self, command_name, *args, **kwargs):
        command = self.commands.get(command_name, None)
        if command is None:
            raise RuntimeError("Can not find command: " + str(command_name))
        command(*args, **kwargs)

    def save_to_json(self, directory, model_name=None):
        uid = uuid.uuid4()
        if model_name is None:
            print("Model will be saved to generated name \"" + str(uid) + "\"")
            model_name = uid

        elif os.path.isdir(directory + "/" + model_name):
            print("Model already exists, current model will be saved to generated name \"" + str(uid) + "\"")
            model_name = uid

        path = directory + "/" + str(model_name)
        os.mkdir(path)
        os.mkdir(path + "/custom")

        with open(path + "/commands.json", 'w') as fp:
            json.dump(self._json_objects['commands'], fp, indent=4)

        with open(path + "/steps.json", 'w') as fp:
            json.dump(self._json_objects['steps'], fp, indent=4)

        with open(path + "/components.json", 'w') as fp:
            ####################################################################
            ## remove any JAX keys from dictionary as they are not serializable
            for i in range(len(self._json_objects['components'])):
                if self._json_objects['components'][i].get("key") != None:
                    del self._json_objects['components'][i]["key"]
            #print(self._json_objects['components'])
            ####################################################################
            json.dump(self._json_objects['components'], fp, indent=4)

        with open(path + "/connections.json", 'w') as fp:
            json.dump(self._json_objects['connections'], fp, indent=4)

        return path, path + "/custom"

    def load_from_dir(self, directory):
        self.make_components(directory + "/components.json", directory + "/custom")
        self.make_connections(directory + "/connections.json")
        self.make_commands(directory + "/commands.json")
        self.make_steps(directory + "/steps.json")
