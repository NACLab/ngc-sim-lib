"""
The utilities file for ngcsimlib
"""
import sys, uuid, os, json
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


def make_unique_path(directory, root_name=None):
    """
    This block of code will make a uniquely named directory inside the specified output folder.
    If the root name already exists it will append a UID to the root name to not overwrite data

    Args:
        directory: The root directory to save models to

        root_name: (Default None) The root name for the model to be saved to,
            if none it will just use the UID

    Returns:
        path to created directory
    """
    uid = uuid.uuid4()
    if root_name is None:
        root_name = str(uid)
        print("generated path will be named \"" + str(root_name) + "\"")

    elif os.path.isdir(directory + "/" + root_name):
        root_name += "_" + str(uid)
        print("root path already exists, generated path will be named \"" + str(root_name) + "\"")

    path = directory + "/" + str(root_name)
    os.mkdir(path)
    return path


def check_serializable(dict):
    """
    Verifies that all the values of a dictionary are serializable

    Args:
        dict: dictionary to check

    Returns:
        list of all the keys that are not serializable
    """
    bad_keys = []
    for key in dict.keys():
        try:
            json.dumps(dict[key])
        except:
            bad_keys.append(key)
    return bad_keys


def extract_args(keywords=None, *args, **kwargs):
    """
    Extracts the given keywords from the provided args and kwargs. This method first finds all the matching keywords
    then for each missing keyword it takes the next value in args and assigns it. It will throw and error if there are
    not enough kwargs and args to satisfy all provided keywords

    Args:
        keywords: a list of keywords to extract

        args: the positional arguments to use as a fallback over keyword arguments

        kwargs: the keyword arguments to first try to extract from

    Returns:
        a dictionary for where each keyword is a key, and the value is assigned
            argument. Will throw a RuntimeError if it fails to match and argument
            to each keyword.
    """
    if keywords is None:
        return None

    a = {key: None for key in keywords}
    missing = []
    for key in keywords:
        if key in kwargs.keys():
            a[key] = kwargs.get(key, None)
        else:
            missing.append(key)

    if len(missing) > len(args):
        raise RuntimeError("Missing arguments")

    else:
        for idx, key in enumerate(missing):
            a[key] = args[idx]

    return a


# Note these are to get a copied hash table of values not the actual compartments
__all_compartments = {}


def Get_Compartment_Batch(compartment_uids=None):
    """
    This method should be used sparingly

    Get a subset of all compartment values based on provided paths. If no paths are provided it will grab all of them

    Args:
        compartment_uids: needed ids

    Returns:
        a subset of all compartment values

    """
    if compartment_uids is None:
        return {key: c.value for key, c in __all_compartments.items()}
    return {key: __all_compartments[key].value for key in compartment_uids}


def Set_Compartment_Batch(compartment_map=None):
    """
    This method should be used sparingly

    Sets a subset of compartments to their corresponding value in the provided dictionary

    Args:
        compartment_map: a map of compartment paths to values
    """
    if compartment_map is None:
        return

    for key, value in compartment_map.items():
        if key not in __all_compartments.keys():
            __all_compartments[key] = value
        else:
            __all_compartments[key].set(value)


def get_compartment_by_name(context, name):
    """
    Gets a specific compartment from a given context

    Args:
        context: context to extract compartment from

        name: name of compartment to get

    Returns: expected compartment, None if not a valid compartment

    """
    return __all_compartments.get(context.path + "/" + name, None)


__component_resolvers = {}
__resolver_meta_data = {}


def get_resolver(class_name, resolver_key):
    """
    A helper method for searching through the resolver list
    """
    return __component_resolvers[class_name + "/" + resolver_key], __resolver_meta_data[class_name + "/" + resolver_key]


def add_component_resolver(class_name, resolver_key, data):
    """
    A helper function for adding component resolvers
    """
    __component_resolvers[class_name + "/" + resolver_key] = data


def add_resolver_meta(class_name, resolver_key, data):
    """
    A helper function for adding component resolvers metadata
    """
    __resolver_meta_data[class_name + "/" + resolver_key] = data


## Contexts
__current_context = ""
__contexts = {"": None}


def get_current_context():
    """
    A helper method for getting the current active context object
    """
    return __contexts[__current_context]


def get_current_path():
    """
    A helper method for getting the current context path
    """
    return __current_context


def get_context(path):
    """
    A helper method for getting a context by a provided path
    """
    return __contexts.get(__current_context + "/" + path, None)


def add_context(name, con):
    """
    A helper method for adding a context to the current path
    """
    __contexts[__current_context + "/" + name] = con


def set_new_context(path):
    """
    A helper method for updating the current active context
    """
    global __current_context
    __current_context = path
