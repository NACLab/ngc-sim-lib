import json
from typing import TYPE_CHECKING, List, Dict, Union, Tuple
from .context_manager import global_context_manager as gcm
from ngcsimlib.logger import warn
from ngcsimlib._src.utils.io import make_unique_path, make_safe_filename
from ngcsimlib._src.modules.modules_manager import modules_manager as modManager
from ngcsimlib._src.operations.BaseOp import BaseOp

from enum import Enum
import os, shutil

from ngcsimlib._src.compartment.compartment import Compartment

if TYPE_CHECKING:
    from .contextAwareObjectMeta import ContextAwareObjectMeta


class ContextObjectTypes(Enum):
    """
    In order for context to compile each of the contextAwareObjects built inside
    of them they need to know what type of object it is. These values are
    expected to be found in the class's _type field. Using decorators found in
    contextObjectDecorators.py will automatically apply these to the classes
    """
    component = "component"
    process = "process"


class Context(object):
    """
    The context object is the container that holds all the information for a
    model. Each context will keep track of all the contextAwareObjects built
    inside of it, and handle some general use cases involving them, such as
    saving and loading. The general pattern is to use a python with block with
    the context to automatically capture each of the contextAwareObjects built
    in side the block. The context will also automatically compile all the
    objects in the correct order (based on compile priority) when leaving the
    with block. This means that in order to use any of the compiled methods or
    processes defined the with block must first be left.
    """
    def __new__(cls, name: str, *args, **kwargs):
        targetPath = gcm.append_path(addition=name)
        if gcm.exists(targetPath):
            return gcm.get_context(targetPath)
        instance = super().__new__(cls)
        gcm.register_context_local(name, instance)
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
        self._connections = {}


    def __enter__(self):
        self.__previous_path = gcm.current_path
        gcm.step_to(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.recompile()
        gcm.step_to(self.__previous_path)
        self.__previous_path = None

    def recompile(self):
        """
        Recompiles all the context aware objects inside the context based on
        their priority. The higher the priority is, the sooner it will happen.
        0 is the default and -1 is reserved for processes and other objects that
        expect all the other objects to be compiled first.

        If custom objects are being made that do not rely on the existing
        metaclasses and decorators, an object can be flagged as compilable by
        giving it the field "_is_compilable" and the priority can be set with
        "_priority".
        """
        priorities = {}

        for objectType in self.objects.keys():
            _objs = self.get_objects_by_type(objectType)
            for objName, obj in _objs.items():
                if getattr(obj, "_is_compilable", False):
                    p = getattr(obj, "_priority", None)
                    p = 0 if p is None else p

                    if p not in priorities:
                        priorities[p] = []
                    priorities[p].append(obj)


        keys = sorted(priorities.keys(), reverse=True)
        for key in keys:
            for obj in priorities[key]:
                obj.compile()

    def registerObj(self, obj: "ContextAwareObjectMeta"):
        """
        Registers an object in the context. The context automatically sorts the
        objects by type through the "_type" field set on the object/class. It
        expects to be given a "ContextObjectType" but it is not a requirement.
        If an unknown type is provided to the context it will still sort it
        into a bin with other objects of the same type. (Note: _type can be
        either a string or ContextObjectTypes.TYPE, both will be grouped
        together)

        Args:
            obj: The object to register, requires the "_type" field to be
                defined and not null
        """
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

        if self.objects[_type].get(obj) is not None:
            warn(f"Trying to register context object with the same name "
                 f"({obj.name}) as another object in this context. Aborting "
                 f"registration!")
            return

        self.objects[_type][obj.name] = obj

    def get_objects_by_type(self, objectType: ContextObjectTypes | str) -> Dict[
        str, "ContextAwareObjectMeta"]:
        """
        Gets the group of objects of the designated type tracked by this
        context.

        Args:
            objectType: The object type to extract from the context

        Returns: A dictionary of str:obj pairs where each key is the name of
            object. Will return an empty dictionary if the given type is not
            found in the context.

        """
        _type = objectType.value if isinstance(objectType,
                                               ContextObjectTypes) else objectType
        return self.objects.get(_type, {})

    def get_objects(self, *object_names: str,
                    objectType: ContextObjectTypes | str,
                    unwrap: bool = True) -> \
        Union[None, "ContextAwareObjectMeta", List[Union[
            "ContextAwareObjectMeta", None]]]:
        """
        Gets a specific group of objects by name and type tracked by this
        context.

        Args:
            *object_names: Any number of object names to extract from the
                context

            objectType: The object type shared by these objects.
            unwrap: In the event that there is a single object found should the
                method return a list of length one or a single value. Will also
                change it from returning an empty list if no names are provided
                to returning None.

        Returns: None or empty list if no names are provided based on if unwrap
            is set to true. Will return either a single object or a list of
            length one if only one name is provided based on unwrap. If multiple
            names are provided, the method will return a list of objects found
            in the context with "None"s where it could not find an object of the
            given name.

        """

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
        Union[None, "ContextAwareObjectMeta", List[Union[
            "ContextAwareObjectMeta", None]]]:
        return self.get_objects(*component_names,
                                objectType=ContextObjectTypes.component,
                                unwrap=unwrap)

    def add_connection(self, source, destination):
        self._connections[destination.root] = source


    def save_to_json(self, directory: str, model_name: Union[str, None] = None,
                     custom_save: bool = True, overwrite: bool = False):
        """
        Saves the context to a collection fo JSON files.

        Args:
            directory: The directory to save the context to
            model_name: The model name to save the context to if none will use
                the context's name
            custom_save: Should this context call the custom save methods on
                each object in the context.
            overwrite: Should this context overwrite a previously saved context
                if no it will append a uuid to the end of the model to ensure it
                doesn't overwrite.
        """
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

        contextMeta = {"types": list(self.objects.keys())}

        with open(f"{path}/contextData.json", "w") as f:
            f.write(json.dumps(contextMeta))

        for _type in self.objects.keys():
            type_path = f"{path}/{make_safe_filename(_type)}"
            os.mkdir(type_path)

            _objs = self.get_objects_by_type(_type)

            made_custom = False
            data = {}

            for obj_name, obj in _objs.items():
                objData = {}
                if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
                    objData.update(obj.to_json())

                objData["modulePath"] = modManager.resolve_public_import(obj)

                data[obj_name] = objData

                if custom_save:
                    if hasattr(obj, "save") and callable(getattr(obj, "save")):
                        if not made_custom:
                            os.mkdir(type_path + "/custom")
                            made_custom = True
                        obj.save(type_path + "/custom")

            with open(f"{type_path}/roots.json", "w") as fp:
                json.dump(data, fp, indent=4)

        connections = {}
        for connectionRoot, source in self._connections.items():
            if isinstance(source, Compartment):
                connections[connectionRoot] = source.target
            else:
                connections[connectionRoot] = source.to_json()

        with open(f"{path}/connections.json", "w") as fp:
            json.dump(connections, fp, indent=4)



    @staticmethod
    def load(directory: str, module_name: str):
        if gcm.exists(gcm.append_path(module_name)):
            warn("Trying to load a context that already exists, returning "
                 "existing context")
            return gcm.get_context(gcm.append_path(module_name))

        with Context(module_name) as ctx:
            path = directory + "/" + module_name
            with open(f"{path}/contextData.json", "r") as f:
                metaData = json.load(f)

            delayed_load = []

            for _type in metaData["types"]:
                type_path = f"{path}/{make_safe_filename(_type)}"
                with open(f"{type_path}/roots.json", "r") as fp:
                    typeRoots = json.load(fp)

                for obj_name, objData in typeRoots.items():
                    objKlass = modManager.import_module(objData["modulePath"])
                    args = objData["args"]
                    kwargs = objData["kwargs"]
                    newObj = objKlass(*args, **kwargs)

                    delayed_load.append((getattr(newObj, "_priority", 0), newObj, objData, type_path))

            delayed_load = sorted(delayed_load, key=lambda x: x[0], reverse=True)
            for _, obj, data, type_path in delayed_load:
                if hasattr(obj, "from_json") and callable(getattr(obj, "from_json")):
                    obj.from_json(objData)

                if hasattr(obj, "load") and callable(getattr(obj, "load")):
                    obj.load(f"{type_path}/custom")


            with open(f"{path}/connections.json", "r") as fp:
                connectionData = json.load(fp)
                for connectionRoot, target in connectionData.items():
                    context_path = ctx.path.split(":")
                    compartment_path = connectionRoot.split(":")
                    component_name = compartment_path[len(context_path)]
                    component = ctx.get_components(component_name, unwrap=True)
                    if hasattr(component, compartment_path[-1]) and isinstance(getattr(component, compartment_path[-1]), Compartment):
                        if isinstance(target, str):
                            getattr(component, compartment_path[-1]).target = target
                        else:
                            getattr(component, compartment_path[-1]).target = BaseOp.load_op(target)

        return ctx



