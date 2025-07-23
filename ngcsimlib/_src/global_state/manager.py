from typing import Union, Any, Dict


class __global_state_manager:
    def __init__(self):
        self.__state = {}
        self.__compartments = {}

    def add_compartment(self, compartment):
        self.__compartments[compartment.root] = compartment

    def get_compartment(self, root):
        return self.__compartments[root]

    @staticmethod
    def make_key(path: str, local_key: str) -> str:
        """
        creates a global key based on the path and local key name
        Args:
            path: the path to the local key
            local_key: the local key name

        Returns: The global key
        """
        return path + ":" + local_key

    def check_key(self, global_key: str) -> bool:
        """
        Checks if the given key is present in the global state
        Args:
            global_key: the key to check

        Returns: if the key is present in the global state

        """
        return global_key in self.__state.keys()

    def add_key(self, path: str, local_key: str, value: any) -> None:
        """
        Adds a key to the global state based
        Args:
            path: the path to the local key
            local_key: the local key name
            value: the value to place in the global state

        Returns:

        """
        self.__state[self.make_key(path, local_key)] = value

    def from_global_key(self, key: str) -> Union[None, Any]:
        """
        Get the value of the given key from the global state
        Args:
            key: the global key

        Returns: the value of the given key, none if the key is not present in
            the global state
        """
        return self.__state.get(key, None)

    def from_local_key(self, path: str, local_key: str) -> Union[None, Any]:
        """
        Parses the global key from the path and local key, then returns the
        value found at that key.

        Args:
            path: The path to the local key
            local_key: the local key name

        Returns:

        """
        return self.from_global_key(self.make_key(path, local_key))

    def set_state(self, state: Dict[str, Any]) -> None:
        """
        Updates the global state with the new state. This new state does not
        need to have all the values present in the global state.
        Args:
            state: The new state to update with
        """
        self.__state.update(state)

    @property
    def state(self) -> dict:
        """
        Returns: a copy of the global state
        """
        return self.__state.copy()

    @state.setter
    def state(self, state: Dict[str, Any]) -> None:
        """
        Updates the global state with the new state.
        Args:
            state: the new state to update with
        """
        self.set_state(state)


global_state_manager = __global_state_manager()
