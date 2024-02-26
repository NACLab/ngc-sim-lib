import sys, uuid, os
from importlib import import_module

_Loaded_Attributes = {}
_Loaded_Modules = {}


def check_attributes(obj, required, fatal=False):
    if required is None:
        return True
    for atr in required:
        if not hasattr(obj, atr):
            if not fatal:
                return False
            raise AttributeError(str(obj.name) + " is missing the required attribute of " + atr)
    return True


def load_module(module_path, match_case=False, absolute_path=False):
    if module_path in _Loaded_Modules.keys():
        return _Loaded_Modules[module_path]
    module_name = None
    if not absolute_path:
        final_mod = module_path.split('.')[-1]
        final_mod = final_mod if match_case else final_mod.lower()

        for module in sys.modules:
            last_mod = module.split('.')[-1]
            last_mod = last_mod if match_case else last_mod.lower()
            if final_mod == last_mod:
                print("Loading module from " + module)
                module_name = module
                break
        if module_name is None:
            raise RuntimeError("Failed to find dynamic import for \"" + module_path + "\"")


    else:
        module_name = module_path

    mod = import_module(module_name)
    _Loaded_Modules[module_path] = mod
    return mod

def load_from_path(path, absolute_path=False, match_case=False):
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
    if attribute_name in _Loaded_Attributes.keys():
        return _Loaded_Attributes[attribute_name]

    mod = load_module(attribute_name if module_path is None else module_path, match_case=match_case, absolute_path=absolute_path)

    attribute_name = attribute_name if match_case else attribute_name[0].upper() + attribute_name[1:]

    try:
        attr = getattr(mod, attribute_name)
    except AttributeError:
        raise RuntimeError("Could not find an attribute with name \"" + attribute_name + "\" in module " + mod.__name__) \
            from None

    _Loaded_Attributes[attribute_name] = attr
    return attr

def make_unique_path(directory, root_name=None):
    """
    This block of code will make a uniquely named directory inside the specified output folder.
    If the root name already exists it will append a UID to the root name to not overwrite data
    :param directory: The root directory to save models to
    :param root_name: (Default None) The root name for the model to be saved to, if none it will just use the UID
    :return: path to created directory
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

###### Preload Modules
def preload(module_path):
    import json
    from types import SimpleNamespace

    with open(module_path, 'r') as file:
        modules = json.load(file, object_hook=lambda d: SimpleNamespace(**d))

    for module in modules:
        mod = import_module(module.absolute_path)
        _Loaded_Modules[module.absolute_path] = mod

        for attribute in module.attributes:
            atr = getattr(mod, attribute.name)
            _Loaded_Attributes[attribute.name] = atr

            _Loaded_Attributes[".".join([module.absolute_path, attribute.name])] = atr
            if hasattr(attribute, "keywords"):
                for keyword in attribute.keywords:
                    _Loaded_Attributes[keyword] = atr


preload(module_path="json_files/preloaded_modules.json")