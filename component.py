from abc import ABC, abstractmethod
import warnings
import NGC_Learn_Core.utils as utils


class _VerboseDict(dict):
    """
    The Verbose Dictionary functions like a traditional python dictionary with more specific warnings and errors.
    Specifically each verbose dictionary logs when new keys are added to it, and when a key is asked for that is not
    present in the dictionary it will throw a runtime error that includes the name (gotten from the component) to make
    it easier during debugging
    """

    def __init__(self, seq=None, name=None, **kwargs):
        seq = {} if seq is None else seq
        name = 'unnamed' if name is None else str(name)

        super().__init__(seq, **kwargs)
        self.name = name

    def __setitem__(self, key, value):
        if key not in self.keys():
            warnings.warn("Adding key \"" + str(key) + "\" to " + self.name)
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if item not in self.keys():
            raise RuntimeError("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                               "\nAvailable compartments " + str(self.keys()))
        return super().__getitem__(item)


class _ComponentMetadata:
    """
    Component Metadata is used to track the incoming and outgoing connections to a component. This is also where the
    root calls exist for verifying that components have the correct number of connections.
    """

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
                str(self.component_name) + " has an incorrect number of incoming connections.\nMinimum connections: " +
                str(min_connections) + "\t Actual Connections: None")

        if compartment in self._incoming_connections.keys():
            count = self._incoming_connections[compartment]
            if min_connections is not None and count < min_connections:
                raise RuntimeError(
                    str(self.component_name) + "has an incorrect number of incoming connections.\nMinimum "
                                               "connections: " +
                    str(min_connections) + "\tActual Connections: " + str(count))
            if max_connections is not None and count > max_connections:
                raise RuntimeError(
                    str(self.component_name) + "has an incorrect number of incoming connections.\nMaximum "
                                               "connections: " +
                    str(max_connections) + "\tActual Connections: " + str(count))

    def check_outgoing_connections(self, compartment, min_connections=None, max_connections=None):
        if compartment not in self._outgoing_connections.keys() and min_connections is not None:
            raise RuntimeError(
                str(self.component_name) + " has an incorrect number of outgoing connections.\nMinimum connections: " +
                str(min_connections) + "\t Actual Connections: None")

        if compartment in self._outgoing_connections.keys():
            count = self._outgoing_connections[compartment]
            if min_connections is not None and count < min_connections:
                raise RuntimeError(
                    str(self.component_name) + " has an incorrect number of outgoing connections.\nMinimum "
                                               "connections: " +
                    str(min_connections) + "\tActual Connections: " + str(count))
            if max_connections is not None and count > max_connections:
                raise RuntimeError(
                    str(self.component_name) + " has an incorrect number of outgoing connections.\nMaximum "
                                               "connections: " +
                    str(max_connections) + "\tActual Connections: " + str(count))


class Component(ABC):
    """
    Components are a foundational part of ngclearn and its component/command structure. In ngclearn all stateful
    parts of a model take the form of components. The internal storage of the state of a component takes one
    of two forms, either as a compartment or as a member variable. The member variables are values such as
    hyperparametes and weights, where the transfer of their individual state from component to component is not needed.
    Compartments on the other hand are where the state information both from and for other components are stored. As
    the components are the stateful pieces of the model they also contain the methods and logic behind advancing their
    internal state forward in time.

    The use of this abstract base class for components is completely optional. There is no part of ngclearn that
    requires its use; however, starting here will provide a good foundation and help avoid errors produced from missing
    attributes. That being said this is not an exhaustive base class. There are some commands such as `Evolve` that
    requires an additional function called `evolve` to be present on the component.
    """

    def __init__(self, name, useVerboseDict=False, **kwargs):
        """
        The only truly required parameter for any component in ngclearn is a name. These names should be unique as there
        will be undefined behavior present if multiple components in a model have the same name.

        :param name: the name of the component
        :param useVerboseDict: a boolean value that controls if a more debug friendly dictionary is used for this
        component's compartments. This dictionary will monitor when new keys are added to the compartments dictionary
        and tell you which component key errors occur on. It is not recommended to have these turned on when training as
        they add additional logic that might cause performance decreases. (default: False)
        :param kwargs: additional keyword arguments. These are not used in the base class, but this is here for future
        use if needed.
        """
        # Component Data
        self.name = name

        self.compartments = _VerboseDict(name=self.name) if useVerboseDict else {}
        self.bundle_rules = {}
        self.sources = []

        # Meta Data
        self.metadata = _ComponentMetadata(name=self.name)

    ##Intialization Methods
    def create_outgoing_connection(self, source_compartment):
        """
        Creates a callback function to a specific compartment of the component. These connections are how other
        components will read specific parts of this components state at run time.
        :param source_compartment: the specific compartment whose state will be returned by the callback function
        :return: a callback function that takes no parameters and returns the state of the specified compartment
        """
        self.metadata.add_outgoing_connection(source_compartment)
        return lambda: self.compartments[source_compartment]

    def create_incoming_connection(self, source, target_compartment, bundle=None):
        """
        Binds callback function to a specific local compartment.

        :param source: The defined callback function generally produced by `create_outgoing_connection`
        :param target_compartment:
        :param bundle:
        :return:
        """
        self.metadata.add_incoming_connection(target_compartment)
        if bundle not in self.bundle_rules.keys():
            self.create_bundle(bundle, bundle)
        self.sources.append((source, target_compartment, bundle))

    def create_bundle(self, bundle_name, bundle_rule_name):
        if bundle_name is not None:
            rule = utils.load_attribute(bundle_rule_name)
            self.bundle_rules[bundle_name] = rule
        else:
            try:
                rule = utils.load_attribute(bundle_rule_name)
            except:
                from .bundle_rules import overwrite
                rule = overwrite
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

    @abstractmethod
    def save(self, directory, **kwargs):
        pass
