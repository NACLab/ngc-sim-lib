import sys
from importlib import import_module
from ngcsimlib.logger import info

## Globally tracking all the modules, and attributes have been dynamically loaded
_Loaded_Attributes = {}
_Loaded_Modules = {}
_Loaded = False
def is_pre_loaded():
    return _Loaded

def set_loaded(val):
    global _Loaded
    _Loaded = val

def check_attributes(obj, required, fatal=False):
    """
    This function will verify that a provided object has the requested attributes.

    Args:
        obj: Object that should have the attributes

        required: A list of required attributes by string name

        fatal: If true an Attribute error will be thrown (default False)

    Returns:
        Boolean only returns if not fatal, if the object has the required attributes
    """
    if required is None:
        return True
    for atr in required:
        if not hasattr(obj, atr):
            if not fatal:
                return False
            if hasattr(obj, "name"):
                raise AttributeError(str(obj.name) + " is missing the required attribute of " + atr)
            else:
                raise AttributeError("Checked object is missing the required attribute of " + atr)
    return True


def load_module(module_path, match_case=False, absolute_path=False):
    """
    Trys to load a module from the provided path.

    Args:
        module_path: Module path, supports compound modules such as `ngcsimlib.commands`

        match_case: If true the module must case match exactly (default false)

        absolute_path: If true tries to import exactly what is passed to module
            path (default false)

    Returns:
        the module that has been loaded
    """
    # Return if we have already loaded this module
    if module_path in _Loaded_Modules.keys():
        return _Loaded_Modules[module_path]
    # Unkown module
    module_name = None
    if absolute_path:
        module_name = module_path
    else:
        # Extract the final module from the module_path
        final_mod = module_path.split('.')[-1]
        final_mod = final_mod if match_case else final_mod.lower()

        # Try to match the final module to any currently loaded module
        for module in sys.modules:
            last_mod = module.split('.')[-1]
            last_mod = last_mod if match_case else last_mod.lower()
            if final_mod == last_mod:
                info("Loading module from " + module)
                module_name = module
                break

        # Will only be None if no imported modules match the import name
        if module_name is None:
            raise RuntimeError("Failed to find dynamic import for \"" + module_path + "\"")

    mod = import_module(module_name)
    _Loaded_Modules[module_path] = mod
    return mod


def load_from_path(path, match_case=False, absolute_path=False):
    """
    Loads an attribute/module from a specified path. If not using the absolute path the module name and attribute
    names will be assumed to be the same.

    Args:
        path: path to attribute/module to load, will try to find the attribute/module if not already loaded

        match_case: If true the module must case match exactly (default false)

        absolute_path: If true tries to import exactly what is passed to module path (default false)

    Returns:
        The attribute at the path
    """
    if absolute_path is True:
        module_name = '.'.join(path.split('.')[:-1])
        class_name = path.split('.')[-1]
        match_case = True
    else:
        module_name = path
        class_name = path

    return load_attribute(module_path=module_name, attribute_name=class_name,
                          match_case=match_case, absolute_path=absolute_path)


def load_attribute(attribute_name, module_path=None, match_case=False, absolute_path=False):
    """
    Loads a specific attribute from a specified module

    Args:
        attribute_name: name of the attribute to load

        module_path: module to load the attribute from, will use the attribute
            name if None (default None)

        match_case: If true the module must case match exactly (default false)

        absolute_path: If true tries to import exactly what is passed to module
            path (default false)

    Returns:
        the loaded attribute
    """
    if attribute_name in _Loaded_Attributes.keys():
        return _Loaded_Attributes[attribute_name]

    if attribute_name is None:
        raise RuntimeError()

    mod = load_module(attribute_name if module_path is None else module_path, match_case=match_case,
                      absolute_path=absolute_path)

    attribute_name = attribute_name if match_case else attribute_name[0].upper() + attribute_name[1:]

    try:
        attr = getattr(mod, attribute_name)
    except AttributeError:
        raise RuntimeError("Could not find an attribute with name \"" + attribute_name + "\" in module " +
                           mod.__name__) \
            from None

    _Loaded_Attributes[attribute_name] = attr
    return attr
