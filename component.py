from abc import ABC, abstractmethod
import warnings
import utils


class _VerboseDict(dict):
    def __init__(self, seq=None, name=None, **kwargs):
        seq = {} if seq is None else seq
        name = 'unnamed' if name is None else str(name)

        super().__init__(seq, **kwargs)

        self.name = name
        self.check_set = True  # DEBUGGING.check_set
        self.check_get = True  # DEBUGGING.check_get

    def __setitem__(self, key, value):
        if self.check_set and key not in self.keys():
            warnings.warn("Adding key \"" + str(key) + "\" to " + self.name,
                          stacklevel=6)  # DEBUGGING.stack_level_warning)
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if self.check_get and item not in self.keys():
            raise RuntimeError("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                               "\nAvailable compartments " + str(self.keys()))
        return super().__getitem__(item)


class _ComponentMetaData:
    def __init__(self, name):
        self.component_name = name
        self._incoming_connections = {}
        self._outgoing_connections = {}

    def add_outgoing_connection(self, compartment_name):
        if compartment_name not in self._outgoing_connections.keys():
            self._outgoing_connections[compartment_name] = 1
        else:
            self._outgoing_connections[compartment_name] += 1

    def add_incoming_connection(self, compartment_name):
        if compartment_name not in self._incoming_connections.keys():
            self._incoming_connections[compartment_name] = 1
        else:
            self._incoming_connections[compartment_name] += 1

    def check_incoming_connections(self, compartment, min_connections=None, max_connections=None):
        if compartment not in self._incoming_connections.keys() and min_connections is not None:
            raise RuntimeError(
                str(self.component_name) + " has an incorrect number of connections.\nMinimum connections: " +
                str(min_connections) + "\t Actual Connections: None")

        if compartment in self._incoming_connections.keys():
            count = self._incoming_connections[compartment]
            if min_connections is not None and count < min_connections:
                raise RuntimeError(
                    str(self.component_name) + " has an incorrect number of connections.\nMinimum connections: " +
                    str(min_connections) + "\tActual Connections: " + str(count))
            if max_connections is not None and count > max_connections:
                raise RuntimeError(
                    str(self.component_name) + " has an incorrect number of connections.\nMaximum connections: " +
                    str(max_connections) + "\tActual Connections: " + str(count))


class Component(ABC):
    def __init__(self, name):
        # Component Data
        self.name = name

        self.compartments = _VerboseDict(name=self.name)
        self.bundle_rules = {}
        self.sources = []

        # Meta Data
        self.metadata = _ComponentMetaData(name=self.name)

        self.create_bundle(None, 'overwrite')
    ##Intialization Methods

    def create_outgoing_connection(self, source_compartment):
        self.metadata.add_outgoing_connection(source_compartment)
        return lambda: self.compartments[source_compartment]

    def create_incoming_connection(self, source, target_compartment, bundle=None):
        self.metadata.add_incoming_connection(target_compartment)
        self.sources.append((source, target_compartment, bundle))

    def create_bundle(self, bundle_name, bundle_rule_name):
        rule = utils.load_attribute(bundle_rule_name)
        self.bundle_rules[bundle_name] = rule

    ## Runtime Methods
    def clamp(self, compartment, value):
        self.compartments[compartment] = value

    def process_incoming(self):
        for (source, target_compartment, bundle) in self.sources:
            yield source(), target_compartment, bundle

    def pre_gather(self):
        pass

    def gather(self):
        self.pre_gather()
        for val, dest_comp, bundle in self.process_incoming():
            self.bundle_rules[bundle](self, val, dest_comp)


    ##Abstract Methods
    @abstractmethod
    def verify_connections(self):
        pass

    @abstractmethod
    def advance_state(self, **kwargs):
        pass

    @abstractmethod
    def reset(self, **kwargs):
        pass