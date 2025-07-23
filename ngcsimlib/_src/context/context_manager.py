from ngcsimlib.logger import warn, info
from typing import Union, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context

Path = Union[List[str], str, None]

class __context_manager:
    def __init__(self, seperator: str = ":"):
        self.__contexts: Dict[str, "Context"] = {}
        self.__current_path: List[str] = []
        self.__seperator: str = seperator

    @property
    def current_context(self) -> Union["Context", None]:
        """
        Returns: The context found at the current path, or none if there is no
            existing context.
        """
        return self.__contexts.get(self.join_path(), None)

    @property
    def current_location(self) -> str:
        """
        Returns: The last segment of the current path
        """
        if len(self.__current_path) == 0:
            return ""
        return self.__current_path[-1]

    @property
    def current_path(self) -> str:
        """
        Returns: The current path of the manager, this does not mean there is a
        context at this path
        """
        return self.join_path()

    def clear(self):
        """
        Clears all the current context. Do not call this unless you know what
        you are doing.
        """
        self.__contexts.clear()

    def step(self, location: str) -> bool:
        """
        Steps one step forward in the hierarchy of contexts
        Args:
            location: The path to step into

        Returns: if there is a registered context at the path stepped into (it will
        still step either way)

        """
        self.__current_path.append(location)
        if self.exists():
            return True
        warn(f"Stepping into a context path that does not have an associated "
             f"context ({self.join_path()}).")
        return False

    def step_back(self) -> bool:
        """
        Steps back one step in the hierarchy of contexts
        Returns: if it successfully stepped back, will be false at the root
        """
        if len(self.__current_path) == 0:
            return False
        self.__current_path.pop()
        return True

    def step_to(self, path: Path) -> bool:
        """
        Steps to a specific path in the hierarchy of contexts
        Args:
            path: The path to step directly too

        Returns: if there is a registered context at the path stepped into (it will
        still step either way)
        """

        _path = self.split_path(path)
        self.__current_path[:] = _path.copy()
        if self.exists():
            return True
        warn(f"Stepping into a context path that does not have an associated "
             f"context ({self.join_path()}).")
        return True

    def get_context(self, path: Path) -> Union["Context", None]:
        """
        Args:
            path (default: None): The path to look for the context, will look at
            the current path if no path is provided

        Returns: the context at the proved path if it exists, otherwise None
        """

        path = self.join_path(path)
        return self.__contexts.get(path, None)

    def exists(self, path: Path = None) -> bool:
        """
        Checks if a path exists in the hierarchy of contexts
        Args:
            path: the path to check, if none checks the current path

        Returns: True if a context exists at the provided path, False otherwise

        """
        _path = path if path is not None else self.__current_path
        _path = self.join_path(_path)
        if _path == "":
            return True
        return _path in self.__contexts.keys()

    def join_path(self, path: Path = None) -> str:
        """
        Converts a path (either a string already or a list of strings) into a
        single string using the seperator char.
        Args:
            path: The path to join into a string

        Returns: The joined path
        """
        if path is None:
            return self.join_path(self.__current_path)
        if isinstance(path, str):
            return path
        return self.__seperator.join(path)

    def split_path(self, path: Path = None) -> List[str]:
        """
        Converts a path (either a string already or a list of strings) into a
        list of strings, based on the seperator char.
        Args:
            path: The path to split into a list

        Returns: The split path
        """
        if path is None:
            return self.__current_path
        if isinstance(path, list):
            return path
        return path.split(self.__seperator)

    def append_path(self, rootPath: Path = None, addition: Path = None) -> str:
        """
        Joins two paths together using the seperator char. If rootPath is none
        it will use the current path.

        Args:
            rootPath: The left hand side of the paths
            addition: The right hand side of the paths

        Returns: The joined paths

        """
        if addition is None:
            return self.join_path(rootPath)

        _path = self.join_path(rootPath)

        if isinstance(addition, list):
            if _path == "":
                return self.join_path(addition)
            return self.join_path(rootPath) + self.__seperator + self.join_path(addition)

        if _path == "":
            return addition if addition is not None else ""
        return _path + self.__seperator + addition

    def register_context(self, path: Path, context: "Context", overwrite: bool = False):
        """
        Registers a context to the set of global contexts starting from the root
        Args:
            path: The path to register the context under
            context: The context to register
            overwrite (default: False): Should this overwrite a context if one
            already exists at that path, will throw a warning either way.

        Returns: if the context was successfully registered
        """

        _path = self.join_path(path)
        if self.exists(_path) and not overwrite:
            warn(f"Attempted to overwrite existing context at path ({_path}). "
                 f"Aborting!")
            return False

        if self.exists(_path):
            warn(f"Overwriting existing context at path ({_path}).")

        self.__contexts[path] = context

    def register_context_local(self, local_path: Path, context: "Context",
                               overwrite: bool = True) -> bool:
        """
        Registers a context to the set of global contexts starting from the current
        path
        Args:
            local_path: The local path to register the context under
            context: The context to register
            overwrite (default: False): Should this overwrite a context if one
            already exists at that path, will throw a warning either way.

        Returns: if the context was successfully registered

        """
        return self.register_context(self.append_path(None, local_path), context, overwrite)

    def remove_context(self, path: Path):
        """
        Unregisters a context to the set of global contexts at the given path
        Args:
            path: The path to unregister the context under

        Returns: if a context was successfully unregistered

        """
        _path = self.join_path(path)
        if self.exists(_path):
            info(f"Unregistering context at path ({_path}).")
            del self.__contexts[_path]
            return True
        else:
            warn(f"Trying to unregister context at path ({_path}), "
                 f"but no context was found.")
            return False

global_context_manager = __context_manager()
