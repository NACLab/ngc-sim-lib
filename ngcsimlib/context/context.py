import json
from typing import TYPE_CHECKING, List, Dict, Union, Tuple
from ._context_manager import append_path, register_context_local, check_exists, \
    get_context, get_current_path, step_to
from ngcsimlib.logger import warn
from ngcsimlib.utils.io import make_unique_path, make_safe_filename
from ngcsimlib.parser.utils import compileObject

from enum import Enum
import os, shutil

if TYPE_CHECKING:
    from .contextObj import ContextObjectMeta


class ContextObjectTypes(Enum):
    component = "component"
    process = "process"


class Context(object):
    def __new__(cls, name: str, *args, **kwargs):
        targetPath = append_path(addition=name)
        if check_exists(targetPath):
            return get_context(targetPath)
        instance = super().__new__(cls)
        register_context_local(name, instance)
        instance.path = targetPath
        instance.__previous_path = None

        return instance

    def __init__(self, name: str):
        if hasattr(self, "_initialized"):
            return
        else:
            self._initialized = True

        self.name = name
        self.objects = {}

    def __enter__(self):
        self.__previous_path = get_current_path()
        step_to(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.recompile()
        step_to(self.__previous_path)
        self.__previous_path = None

    def recompile(self):
        priorities = {}


        for objectType in self.objects.keys():
            _objs = self.get_objects_by_type(objectType)
            for onjName, obj in _objs.items():
                if getattr(obj, "_is_compilable", False) and hasattr(obj, "_priority"):
                    p = obj._priority if obj._priority is not None else 0
                    if p not in priorities:
                        priorities[p] = []
                    priorities[p].append(obj)

        keys = sorted(priorities.keys(), reverse=True)
        for key in keys:
            for obj in priorities[key]:
                obj.compile()

    def registerObj(self, obj: "ContextObjectMeta"):
        _type = getattr(obj, "_type", None)
        if _type is None:
            warn(f"When registering object {obj} no context object type "
                 f"was found. Functionality between the context and the "
                 f"object will be limited. Please use one of the provided "
                 f"context object types or define your own to ensure "
                 f"compatability")
            return

        if not isinstance(_type, ContextObjectTypes) and not (
            isinstance(_type, str) and _type in ContextObjectTypes.__members__):
            warn(
                f"Context object type {_type} is not known to this context. It will "
                f"be stored and tracked but some functionality will be "
                f"missing. If you don't know what this message means make "
                f"sure that your context objects are being decorated by one "
                f"of the context ObjectType decorators")
        if isinstance(_type, ContextObjectTypes):
            _type = _type.value

        if _type not in self.objects.keys():
            self.objects[_type] = {}

        self.objects[_type][obj.name] = obj

    def get_objects_by_type(self, objectType: ContextObjectTypes | str) -> Dict[
        str, "ContextObjectMeta"]:
        _type = objectType.value if isinstance(objectType,
                                               ContextObjectTypes) else objectType
        return self.objects[_type]

    def get_objects(self, *object_names: str,
                    objectType: ContextObjectTypes | str,
                    unwrap: bool = True) -> \
        Union[None, "ContextObjectMeta", List[Union["ContextObjectMeta", None]]]:

        if len(object_names) == 0:
            return None if unwrap else []

        _all_objects = self.get_objects_by_type(objectType)
        _objs = []
        for component_name in object_names:
            _objs.append(_all_objects.get(component_name, None))

        for name, obj in zip(object_names, _objs):
            if obj is None:
                warn(
                    f"Could not find an {objectType} with the name \"{name}\" in the context")

        if len(_objs) == 1 and unwrap:
            return _objs[0]
        return _objs

    def get_components(self, *component_names: str, unwrap: bool = True) -> \
    Union[None, "ContextObjectMeta", List[Union["ContextObjectMeta", None]]]:
        return self.get_objects(*component_names,
                                objectType=ContextObjectTypes.component,
                                unwrap=unwrap)


    def save_to_json(self, directory, model_name: Union[str, None] = None,
                     custom_save: bool = True, overwrite: bool = False):
        if model_name is None:
            model_name = self.name
        model_name = make_safe_filename(model_name)

        if overwrite and os.path.isdir(directory + "/" + model_name):
            for filename in os.listdir(directory + "/" + model_name):
                file_path = os.path.join(directory + "/" + model_name, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
            shutil.rmtree(directory + "/" + model_name)


        path = make_unique_path(directory, model_name)


        #TODO: Modules

        for _type in self.objects.keys():
            type_path = f"{path}/{make_safe_filename(_type)}"
            os.mkdir(type_path)

            _objs = self.get_objects_by_type(_type)

            made_custom = False
            data = {}

            for obj_name, obj in _objs.items():
                if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
                    data[obj_name] = obj.to_json()

                if custom_save:
                    if hasattr(obj, "custom_save") and callable(getattr(obj, "custom_save")):
                        if not made_custom:
                            os.mkdir(type_path + "/custom")
                            made_custom = True
                        obj.custom_save(type_path + "/custom")

            with open(f"{type_path}/roots.json", "w") as fp:
                json.dump(data, fp, indent=4)



