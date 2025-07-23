import sys
import importlib


class __ModulesManager:
    def __init__(self):
        self.__loaded_attributes = {}
        self.__loaded_modules = {}
        self.__needed_imports = set()

    def resolve_public_import(self, obj, top_level_module=None):
        """
        Try to find the shortest import path for `obj` under `top_level_module`.
        """
        cls = obj if isinstance(obj, type) else type(obj)

        if top_level_module is None:
            top_level_module = obj.__module__.split('.')[0]

        mod = sys.modules[top_level_module]
        for attr_name in dir(mod):
            if getattr(mod, attr_name) is cls:
                return (f"{top_level_module}.{attr_name}")
        return f"{cls.__module__}.{cls.__qualname__}"


    def import_module(self, mod: str):
        parts = mod.split(".")
        for i in range(len(parts), 0, -1):
            module_name = ".".join(parts[:i])
            try:
                module = importlib.import_module(module_name)
                break
            except ImportError:
                continue
        else:
            raise ImportError(f"Could not import module '{mod}'")

        obj = module
        for attr in parts[i:]:
            obj = getattr(obj, attr)
        return obj

    def resolve_imports(self, *objs):
        for obj in objs:
            self.__needed_imports.add(self.resolve_public_import(obj))

    def get_needed_imports(self):
        return self.__needed_imports

modules_manager = __ModulesManager()