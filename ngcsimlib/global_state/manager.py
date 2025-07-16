from typing import Union, Any, Dict


class __global_state_manager:
    def __init__(self):
        self.__state = {}

    @staticmethod
    def make_key(path: str, key: str) -> str:
        return path + ":" + key

    def check_key(self, key: str) -> bool:
        return key in self.__state.keys()

    def add_key(self, path: str, key: str, value: any) -> None:
        self.__state[self.make_key(path, key)] = value

    def from_key(self, key: str) -> Union[None, Any]:
        return self.__state.get(key, None)

    def get_value(self, path: str, key: str) -> Union[None, Any]:
        return self.from_key(self.make_key(path, key))

    def set_state(self, state: Dict[str, Any]) -> None:
        self.__state.update(state)

    @property
    def state(self) -> dict:
        return self.__state.copy()


global_state_manager = __global_state_manager()