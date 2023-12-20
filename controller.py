from utils import load_attribute, check_attributes, load_from_path
import json, uuid

class Controller:
    def __init__(self):
        self.steps = []
        self.components = {}
        self.connections = []

    def runCycle(self, **kwargs):
        for step in self.steps:
            step(**kwargs)

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

    def add_step(self, step_type, *args, match_case=False, absolute_path=False, components=None, **kwargs):
        Step = load_from_path(path=step_type, match_case=match_case, absolute_path=absolute_path)
        if not callable(Step):
            raise RuntimeError("The object named \"" + Step.__name__ + "\" is not callable. Please make sure "
                                                                       "the object is callable and returns a "
                                                                       "callable object")
        if components is not None:
            components = [self.components[name] for name in components]
        self.steps.append(Step(*components, *args, **kwargs))

    def add_component(self, component_type, *args, match_case=False, absolute_path=False, **kwargs):
        Component_class = load_from_path(path=component_type, match_case=match_case, absolute_path=absolute_path)

        component = Component_class(*args, **kwargs)
        check_attributes(component, ["name", "verify_connections"], fatal=True)
        self.components[component.name] = component


