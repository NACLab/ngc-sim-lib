from utils import load_attribute, check_attributes
import json


class Controller:
    def __init__(self):
        self.steps = []
        self.components = {}
        self.connections = []

    def runCycle(self, **kwargs):
        for step in self.steps:
            step(**kwargs)

    def add_component(self, component):
        check_attributes(component, ["name", "verify_connections"], fatal=True)
        self.components[component.name] = component

    def verify_cycle(self):
        for component in self.components.keys():
            self.components[component].verify_connections()

    def connect(self, source_component, source_compartment, target_component, target_compartment, bundle=None):
        self.components[target_component].create_incoming_connection(
            self.components[source_component].create_outgoing_connection(source_compartment), target_compartment, bundle)
        self.connections.append((source_component, source_compartment, target_component, target_compartment, bundle))

    def make_connections(self, path_to_cables_file):
        with open(path_to_cables_file, 'r') as file:
            cables = json.load(file)
            for cable in cables:
                self.connect(**cable)

    def add_step(self, step_type, *args, match_case=False, absolute_path=False, **kwargs):
        if absolute_path is True:
            module_name = '.'.join(step_type.split('.')[:-1])
            class_name = step_type.split('.')[-1]
            match_case = True
        else:
            module_name = step_type
            class_name = step_type

        Step = load_attribute(module_path=module_name, attribute_name=class_name,
                              match_case=match_case, absolute_path=absolute_path)

        if not callable(Step):
            raise RuntimeError("The object named \"" + Step.__name__ + "\" is not callable. Please make sure "
                                                                       "the object is callable and returns a "
                                                                       "callable object")
        self.steps.append(Step(*args, **kwargs))
