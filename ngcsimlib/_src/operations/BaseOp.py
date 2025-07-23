from ngcsimlib._src.compartment.compartmentMeta import CompartmentMeta
from ngcsimlib._src.modules.modules_manager import modules_manager as modManager
from ngcsimlib._src.global_state.manager import global_state_manager as gsm

import ast

class BaseOp(metaclass=CompartmentMeta):
    """
    The base class for all operations. These allow for inline transformations of
    values as they are passed between components. They are all set up as
    pseudo-compartments but do not actually have a value in the global state.
    """
    def __init__(self, *comps):
        self._comps = list(comps)
        self.astOp = None

    def get(self):
        """
        Returns: The computed value of the operation
        """
        return self._get_value()

    def _get_value(self):
        """
        This is the method that every new operation will need to implement.
        Returns: the result of the operation
        """
        return NotImplemented

    def _to_ast(self, node, ctx):
        """
        This is the method that will be used to compile the operation. Since
        the compiler uses abstract syntax trees it needs to know how to convert
        the given operation into a node on the syntax tree.
        Args:
            node: The node in the tree this is replacing
            ctx: the name of the global state object for referencing values in
                the global state

        Returns: the ast expression needed to run the operation
        """

        if len(self._comps) == 1:
            return self._comps[0]._to_ast(node, ctx)

        inners = [comp._to_ast(node, ctx) for comp in self._comps]
        left = inners[0]
        for inner in inners[1:]:
            left = ast.BinOp(left=left, op=self.astOp, right=inner)

        return left

    def to_json(self):
        data = {'modulePath': modManager.resolve_public_import(self),
                'compartments': []}

        for comp in self._comps:
            if isinstance(comp, BaseOp):
                data['compartments'].append(comp.to_json())
            else:
                data['compartments'].append(comp.root)

        return data


    def get_needed_keys(self):
        """
        Returns: All the keys needed for this operation
        """
        keys = set()
        for comp in self._comps:
            keys.union(comp.get_needed_keys())
        return keys


    def from_json(self, data):
        compartment_paths = data['compartments']
        for compartment_path in compartment_paths:
            if isinstance(compartment_path, str):
                self._comps.append(gsm.get_compartment(compartment_path))
            else:
                self._comps.append(BaseOp.load_op(compartment_path))


    def __rshift__(self, other):
        if any(isinstance(base, CompartmentMeta) for base in type(other).__mro__):
            other.__rrshift__(self)

    @staticmethod
    def load_op(op):
        klass = modManager.import_module(op['modulePath'])
        newOp = klass()
        newOp.from_json(op)
        return newOp