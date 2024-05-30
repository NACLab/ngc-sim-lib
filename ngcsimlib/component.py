from abc import abstractmethod
from ngcsimlib.metaComponent import MetaComponent
from ngcsimlib.compartment import Compartment


class Component(metaclass=MetaComponent):
    """
    Components are a foundational part of ngclearn and its component/command
    structure. In ngclearn, all stateful parts of a model take the form of
    components. The internal storage of the state within a component takes one
    of two forms, either as a compartment or as a member variable. The member
    variables are values such as hyperparameters and weights/synaptic efficacies,
    where the transfer of their individual state from component to component is
    not needed.
    Compartments, on the other hand, are where the state information, both from
    and for other components, are stored. As the components are the stateful
    pieces of the model, they also contain the methods and logic behind advancing
    their internal state (values) forward in time.
    """

    def __init__(self, name, **kwargs):
        """
        The only truly required parameter for any component in ngclearn is a
        name value. These names should be unique; otherwise, there will be
        undefined behavior present if multiple components in a model have the
        same name.

        Args:
            name: the name of the component

            kwargs: additional keyword arguments. These are not used in the base class,
                but this is here for future use if needed.
        """
        # Component Data
        self.name = name


    ##Intialization Methods

    ## Runtime Methods
    def clamp(self, compartment, value):
        """
        Sets a value of a compartment to the provided value

        Args:
            compartment: targeted compartment

            value: provided Value
        """
        if hasattr(self, compartment) and Compartment.is_compartment(getattr(self, compartment)):
            getattr(self, compartment).set(value)

    ##Abstract Methods
    @abstractmethod
    def advance_state(self, **kwargs):
        """
        An abstract method to advance the state of the component to the next one
        (a component transitions from its current state at time t to a new one
        at time t + dt)
        """
        pass

    @abstractmethod
    def reset(self, **kwargs):
        """
        An abstract method that should be implemented to models can be returned
        to their original state.
        """
        pass

    @abstractmethod
    def save(self, directory, **kwargs):
        """
        An abstract method to save component specific state to the provided
        directory

        Args:
            directory:  the directory to save the state to
        """
        pass
