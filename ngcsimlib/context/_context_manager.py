from ngcsimlib.logger import warn, info
from typing import Union, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context

__global_contexts: Dict[str, "Context"] = {}
__current_path: List[str] = []


## Helpers
def _exists(path: Union[str, List[str]] = None) -> bool:
    _path = path if path is not None else _to_path()
    if _path == "":
        return True
    return _path in __global_contexts.keys()


def _to_path(path: Union[str, List[str]] = None) -> str:
    if path is None:
        return _join_path(__current_path)
    return _join_path(path) if isinstance(path, list) else path

def _from_path(path: Union[str, List[str]] = None) -> List[str]:
    if path is None:
        _from_path(__current_path)
    if isinstance(path, list):
        return path

    return path.split(":")


def _join_path(path: Union[List[str], None] = None) -> str:
    if path is None:
        return _join_path(__current_path)
    return ":".join(path)


def append_path(path: Union[str, List[str]] = None,
                addition: Union[str, List[str]] = None) -> str:
    if addition is None:
        return _join_path(path)
    _path = _to_path(path)
    if isinstance(addition, list):
        return _path + _join_path(addition)
    else:
        if _path == "":
            return addition if addition is not None else ""
        _path = _path + ":" + addition
    return _path


## Accessors
def check_exists(path: Union[str, List[str]] = None) -> bool:
    return _exists(path)


def get_context(path: Union[str, List[str]] = None) -> Union["Context", None]:
    if path is None:
        return get_current_context()
    _path = _to_path(path)
    if not _exists(_path):
        warn(f"No context found at {_path}")
        return None
    return __global_contexts.get(_path, None)


def get_current_path() -> str:
    return _join_path()


def get_current_loc() -> str:
    if len(__current_path) == 0:
        return ""
    return __current_path[-1]


def get_current_context() -> Union["Context", None]:
    if not _exists():
        warn(f"Something has gone wrong, there is no context at the current "
             f"context path ({__current_path}).")

    return __global_contexts.get(_join_path(), None)


## Data Control
def register_context_absolute(absolute_path: Union[list, str],
                              context: "Context",
                              overwrite: bool = True) -> bool:
    _path = _join_path(absolute_path) if isinstance(absolute_path,
                                                    list) else absolute_path

    if _exists(_path):
        if overwrite:
            warn(f"Overwriting existing context at path ({_path}).")
            __global_contexts[_path] = context
            return True
        else:
            warn(f"Attempted to overwrite existing context at path ({_path}). "
                 f"Aborting!")
            return False
    __global_contexts[_path] = context
    return True


def register_context_local(local_path: Union[list, str], context: "Context",
                           overwrite: bool = True) -> bool:
    _path = _to_path() + _to_path(local_path)
    return register_context_absolute(_path, context, overwrite)


def unregister_context(path: Union[list, str]) -> bool:
    _path = _join_path(path) if isinstance(path, list) else path
    if _exists(_path):
        info(f"Unregistering context at path ({_path}).")
        del __global_contexts[_path]
        return True
    else:
        warn(f"Trying to unregister context at path ({_path}), "
             f"but no context was found.")
        return False


## Path Control

def clear_current_path() -> None:
    __current_path.clear()


def step_back() -> bool:
    if len(__current_path) == 0:
        __current_path.pop()
        return True
    return False


def step_into(loc: str) -> bool:
    __current_path.append(loc)
    if not _exists():
        warn(f"Stepping into a context path that does not have an associated "
             f"context ({_join_path()}).")
        return False
    return True


def step_to(path: Union[str, List[str]]) -> bool:
    _path = _from_path(path)
    __current_path[:] = _path.copy()
    if not _exists():
        warn(f"Stepping into a context path that does not have an associated "
             f"context ({_join_path()}).")
        return False
    return True
