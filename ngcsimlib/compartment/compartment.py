from .compartmentMeta import CompartmentMeta
from ngcsimlib.global_state.manager import global_state_manager as gState
import ast

from ngcsimlib.operations import BaseOp


class Compartment(metaclass=CompartmentMeta):
    def __init__(self, initial_value):
        self._initial_value = initial_value

        self.name = None
        self._root_target = None
        self._target = self._root_target

    def _setup(self, objName, compName, path):
        self.name = compName
        self._root_target = path + ":" + objName + ":" + self.name
        # self._root_target = objName + ":" + self.name
        self._target = self._root_target
        self.set(self._initial_value)

    def set(self, value):
        gState.set_state({self.target: value})

    def get(self):
        return self._get_value()

    def _get_value(self):
        return gState.from_key(self.target)

    def __jax_array__(self):
        return self.get()

    def __str__(self):
        return str(self._get_value())

    def _to_ast(self, node, ctx):
        if isinstance(self.target, str):
            return ast.Subscript(
                value=ast.Name(id=ctx, ctx=ast.Load()),
                slice=ast.Constant(value=self.target),
                ctx=node.ctx
            )
        return self.target._to_ast(node, ctx)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if isinstance(value, (str, BaseOp)):
            self._target = value
            return

        if isinstance(value, Compartment):
            self._target = value.target
            return

        raise ValueError("Invalid compartment target ", value)