from ngcsimlib.operations import BaseOp, overwrite
from ngcsimlib.utils import Set_Compartment_Batch, get_current_path
from ngcsimlib.logger import error
import uuid


class Compartment:
    """
    Compartments in ngcsimlib are container objects for storing the stateful
    values of components. Compartments are
    tracked globaly and are automatically linked to components and methods
    during compiling to allow for stateful
    mechanics to be run without the need for the class object. Compartments
    also provide an entry and exit point for
    values inside of components allowing for cables to be connected for
    sending and receiving values.
    """

    @classmethod
    def is_compartment(cls, obj):
        """
        A method for verifying if a provided object is a compartment. All
        compartments have `_is_compartment` set to
        true by default and this is

        Args:
            obj: The object to check if it is a compartment

        Returns:
            boolean if the provided object is a compartment
        """
        return hasattr(obj, "_is_compartment")

    def __init__(self, initial_value=None, static=False, is_input=False):
        """
        Builds a compartment to be used inside a component. It is important
        to note that building compartments
        outside of components may cause unexpected behavior as components
        interact with their compartments during
        construction to finish initializing them.
        Args:
            initial_value: The initial value of the compartment. As a general
            practice it is a good idea to
                provide a value that is similar to the values that will
                normally be stored here, such as an array of
                zeros of the correct length. (default: None)

            static: a flag to lock a compartment to be static (default: False)
        """
        self._is_compartment = True
        self.__add_connection = None
        self._static = static
        self.value = initial_value
        self._uid = uuid.uuid4()
        self.name = None
        self.path = None
        self.is_input = is_input
        self._is_destination = False

    def _setup(self, current_component, key):
        """
        Finishes initializing the compartment, called by the component that
        builds the compartment
        (Handled automatically)
        """
        self.__add_connection = current_component.add_connection
        self.name = current_component.name + "/" + key
        self.path = get_current_path() + "/" + self.name
        Set_Compartment_Batch({str(self.path): self})

    def set(self, value):
        """
        Sets the value of the compartment if it not static (Raises a runtime
        error)
        Args:
             value: the new value to be set
        """
        if not self._static:
            self.value = value
        else:
            error("Can not assign value to static compartment")

    def clamp(self, value):
        """
        A wrapper for the set command
        """
        self.set(value)

    def __repr__(self):
        """
        Returns:
             returns the name of the compartment
        """
        return f"[{self.name}]"

    def __str__(self):
        """
        Returns:
             returns the string representation of the value of the compartment
        """
        return str(self.value)

    def __lshift__(self, other) -> None:
        """
        Overrides the left shift operation to be used for wiring compartments
        into one another
        if other is not an Operation it will create an overwrite operation
        with other as the argument,
        otherwise it will use the provided operation

        Args:
            other: Either another component or an instance of BaseOp
        """
        if isinstance(other, BaseOp):
            other.set_destination(self)
            self.__add_connection(other)
        else:
            op = overwrite(other)
            op.set_destination(self)
            self.__add_connection(op)

        self._is_destination = True

    def is_wired(self):
        """
        Returns: if this compartment not marked as an input, or is marked and
        has an input

        """
        if not self.is_input:
            return True

        return self._is_destination
