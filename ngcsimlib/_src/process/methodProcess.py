from ngcsimlib._src.parser.utils import CompiledMethod
from ngcsimlib._src.global_state.manager import global_state_manager
from ngcsimlib._src.context.context_manager import global_context_manager
from ngcsimlib._src.process.baseProcess import BaseProcess

import ast
from typing import Dict, Any, Tuple, List


class MethodProcess(BaseProcess):
    """
    The process in ngcsimlib is the tool used to compile together a set of
    components and methods. As a context aware object processes hook into the
    compile step of all context aware objects but have the priority of -1, so
    they should always compile after all components have been compiled.

    Building a process follows a chain-like process. After initializing the
    process it is possible to chain `.then` calls one after another to build the
    steps of the process (this is can also be accomplished with `>>`). After
    all the steps of the process are set, nothing happens until it is time to
    compile the process.

    Compiling the process goes through and extracts the body of each compiled
    method in its order and pieces them together into a single large method
    call. The resulting method is a pure function that takes in state and
    loop_args returns the updated state.

    To make use of this compiled process simply invoke `.run` and it will use
    the compiled method. If just the compiled method itself is needed calling
    `.run.compiled` will provide direct access.
    """

    def __init__(self, name):
        super().__init__(name)
        self.method_order = []


    def then(self, method):
        """
        Used to specify the order of operations inside the process.
        Args:
            method: The compilable method to run next in the process sequence

        Returns: this process for easy chaining
        """
        self.method_order.append((method.__self__, method.__name__))
        return self

    def __rshift__(self, method):
        return self.then(method)

    def _parse(self) -> Tuple[List, List, List, Dict]:
        bodies = []
        extras = []
        key_set = set()
        for obj, method in self.method_order:
            m: CompiledMethod = getattr(obj, method).compiled
            obj_ast = m.ast
            if not isinstance(obj_ast, ast.Module):
                continue

            for arg in obj_ast.body[0].args.args:
                if arg.arg != "ctx":
                    key_set.add(arg.arg)


            body = obj_ast.body[0].body[:-1]
            bodies.extend(body)
            extras.extend(m.auxiliary_ast)

        namespace = {k: v for obj, method_name in self.method_order for k, v
                        in
                        getattr(obj, method_name).compiled.namespace.items()}

        return bodies, extras, list(key_set), namespace


    def to_json(self) -> Dict[str, Any]:
        """
        This method returns dictionary of data to be saved in the json file that
        will be used to rebuild this object.

        Returns: A dictionary of data that can be serialized by JSON.
        """
        data = {"args": [self.name],
                "kwargs": {},
                "method_order": [
                        {"name": obj.name, "method": method} for obj, method in self.method_order
                    ],
                "watch_list": [
                    compartment.root for compartment in self._watch_list
                ]

                }
        return data

    def from_json(self, data: Dict[str, Any]) -> None:
        method_order = data.get("method_order", [])
        ctx = global_context_manager.current_context
        for step in method_order:
            comp = ctx.get_components(step['name'])
            if comp is not None and hasattr(comp, step['method']):
                self.then(getattr(comp, step['method']))

        watch_list = data.get("watch_list", [])
        for compartment_root in watch_list:
            self.watch(global_state_manager.get_compartment(compartment_root))