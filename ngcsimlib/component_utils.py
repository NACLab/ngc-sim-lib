import warnings

class VerboseDict(dict):
    """
    The Verbose Dictionary functions like a traditional python dictionary with
    more specific warnings and errors.
    Specifically each verbose dictionary logs when new keys are added to it,
    and when a key is asked for that is not present in the dictionary, it will
    throw a runtime error that includes the name (retrieved from an ngcsimlib
    component) to make debugging/tracing easier.

    Args:
        seq: sequence of items to add to the verbose dictionary

        name: the string name of this verbose dictionary

        kwargs: the keyword arguments to first try to extract from
    """

    def __init__(self, seq=None, name=None, verboseDict_showSet=False, verboseDict_autoMap=False,
                 componentClass=None, **kwargs):
        seq = {} if seq is None else seq
        name = 'unnamed' if name is None else str(name)
        super().__init__(seq, **kwargs)
        self.name = name
        self.componentClass = componentClass

        self.showSet = verboseDict_showSet
        self.autoMap = verboseDict_autoMap

        self.mapping = {}

    def __setitem__(self, key, value):
        if key in self.mapping.keys():
            return super().__setitem__(self.mapping[key], value)

        if key in self.keys() or not self.autoMap:
            return super().__setitem__(key, value)

        successful, cname = find_compartment(self, self.componentClass, key)

        if not successful or cname is None:
            return super().__setitem__(key, value)

        warnings.warn("Failed to find compartment \"" + str(key) + "\" in " + self.name +
                      "\nThe correct compartment for \"" + str(key) + "\" is " + str(cname) +
                      "\nMapping \"" + str(key) + "\" to \"" + str(cname) + "\"")
        self.mapping[key] = cname
        return super().__setitem__(self.mapping[key], value)

    def __getitem__(self, item):
        if item in self.mapping.keys():
            return super().__getitem__(self.mapping[item])

        if item in self.keys():
            return super().__getitem__(item)

        successful, cname = find_compartment(self, self.componentClass, item)

        if not successful:
            raise RuntimeError("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                               "\nAvailable compartments " + str(self.keys()))

        if cname is None:
            raise RuntimeError("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                               "\n\"" + str(item) + "\" is a property of " + self.name +
                               ", but unable to find key for requested compartment based on property name"
                               "\nAvailable compartments " + str(self.keys()))

        if not self.autoMap:
            raise RuntimeError("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                               "\nThe correct compartment for \"" + str(item) + "\" is " + str(cname) +
                               "\nAll available compartments " + str(self.keys()))
        warnings.warn("Failed to find compartment \"" + str(item) + "\" in " + self.name +
                      "\nThe correct compartment for \"" + str(item) + "\" is " + str(cname) +
                      "\nMapping \"" + str(item) + "\" to \"" + str(cname) + "\"")
        self.mapping[item] = cname
        return super().__getitem__(self.mapping[item])


class ComponentMetadata:
    """
    Component Metadata is used to track the incoming and outgoing connections
    to a component. This is also where all of the root calls exist for verifying
    that components have the correct number of connections.

    Args:
        name: the string name of this component metadata object
    """

    def __init__(self, name, **kwargs):
        self.component_name = name
        self._incoming_connections = {}
        self._outgoing_connections = {}

    def add_outgoing_connection(self, compartment_name):
        """
        Adds an outgoing connection ("cable") to this component to a compartment
        in a node/component elsewhere.

        Args:
            compartment_name: compartment target in an outgoing component/node
        """
        if compartment_name not in self._outgoing_connections.keys():
            self._outgoing_connections[compartment_name] = 1
        else:
            self._outgoing_connections[compartment_name] += 1

    def add_incoming_connection(self, compartment_name):
        """
        Adds an incoming connection ("cable") to this component from a compartment
        in a node/component elsewhere.

        Args:
            compartment_name: compartment source in an incoming component/node
        """
        if compartment_name not in self._incoming_connections.keys():
            self._incoming_connections[compartment_name] = 1
        else:
            self._incoming_connections[compartment_name] += 1

    def check_incoming_connections(self, compartment, min_connections=None, max_connections=None):
        """
        Checks/validates the incoming information source structure/flow into this component.

        Args:
            compartment: compartment from incoming source to check

            min_connections: minimum number of incoming connections this component should receive

            max_connections: maximum number of incoming connections this component should receive
        """
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
        """
        Checks/validates the outgoing information structure/flow from this component.

        Args:
            compartment: compartment from incoming source to check

            min_connections: minimum number of incoming connections this component should receive

            max_connections: maximum number of incoming connections this component should receive
        """
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


def find_compartment(values, componentClass, compartmentName):
    """
    Offers a utility to search for a compartment in a component. Will automatically
    search for "providedName" + "CompartmentName" as a method on the provided component.
    If that exists it will return the value of that method as the compartment name
    to use inplace of the provided one.
    :param values: The dictionary representing the compartments
    :param componentClass: The class for the component
    :param compartmentName: The compartment name to look for
    :return: a tuple, the first value is a boolean representing if the provided
    compartmentName is either a valid name or a property of the component.
    the second value is either the presumed associated compartment or None if it
    could not match one.
    """
    if compartmentName in values.keys():
        return True, compartmentName

    if not isinstance(getattr(componentClass, compartmentName, None), property):
        return False, None

    nameGetter = getattr(componentClass, compartmentName + "CompartmentName", None)

    if nameGetter is None:
        return True, None

    return True, nameGetter()
