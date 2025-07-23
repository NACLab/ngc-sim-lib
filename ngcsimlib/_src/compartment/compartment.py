from .compartmentMeta import CompartmentMeta
from ngcsimlib._src.global_state.manager import global_state_manager as gState
from ngcsimlib._src.logger import warn
import ast
from typing import TypeVar, Union
from ngcsimlib._src.operations.BaseOp import BaseOp
from ngcsimlib._src.context.context_manager import global_context_manager as gcm

T = TypeVar('T')

class Compartment(metaclass=CompartmentMeta):
    """
    Compartments exist as a layer between the global state of models and the
    use defined objects. At their core they function akin to pointers where
    each compartment stores a key that can be used to access a value in the
    global state. If another compartment is wired into a compartment only the
    target the compartment is pointing to changes, as such their build value in
    the global state will no longer change (it will still exist but just
    nothing will access it unless the user manually goes looking for it). The
    compartment should be reflected in the global state immediately after it is
    initialized. Compartments can be flagged as fixed which means that they
    exist in the global state and can be used in compiled methods but they can
    not be changed after creation.

    Args
        initial_value: the initial value to set in the global state

        fixed (default=False): sets the flag for if this compartment is fixed.
    """
    def __init__(self, initial_value: T, fixed: bool = False):
        self._initial_value = initial_value

        self.name = None
        self._root_target = None
        self._target = self._root_target
        self._fixed = fixed

    @property
    def root(self):
        return self._root_target

    @property
    def targeted(self) -> bool:
        return self._target != self._root_target

    @property
    def fixed(self) -> bool:
        """
        Returns: if this compartment is a fixed value.
        """
        return self._fixed

    def _setup(self, objName, compName, path):
        self.name = compName
        self._root_target = path + ":" + objName + ":" + self.name
        self._target = self._root_target
        self.set(self._initial_value)
        gState.add_compartment(self)

    def set(self, value: T) -> None:
        """
        Sets the value that this compartment is pointing to in the global state.
        This method will abort if either the compartment is flagged as fixed or
        the compartment is not pointing to the compartment assigned to it. This
        would be the case if something was wired into this compartment.

        Args:
            value: The value to set in the global state.
        """
        if self._fixed:
            warn(f"Attempting to set {self._root_target} which is a fixed compartment. Aborting!")
            return
        if self.target != self._root_target:
            warn(f"Attempting to set {self.target} in {self._root_target}. Aborting!")
            return
        gState.set_state({self.target: value})

    def get(self) -> T:
        """
        Returns: The value that this compartment is pointing to in the global state.
        """
        return self._get_value()

    def get_needed_keys(self):
        if isinstance(self.target, BaseOp):
            return self.target.get_needed_keys()
        return set(self.target)

    def _get_value(self):
        if isinstance(self.target, BaseOp):
            return self.target.get()

        return gState.from_global_key(self.target)

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

    def __rrshift__(self, other):
        gcm.current_context.add_connection(other, self)
        self.target = other

    def __rshift__(self, other):
        if isinstance(other, Compartment):
            other.__rrshift__(self)

    @property
    def target(self):
        """
        Returns: the current target of the compartment
        """
        return self._target

    @target.setter
    def target(self, value: Union["Compartment", "BaseOp", str]):
        """
        Sets the target of the compartment to the provided value. It will fail
        if the value is not either another compartment or an operation.

        Args:
            value: The value to target this compartment at.
        """
        if isinstance(value, (str, BaseOp)):
            self._target = value
            return

        if isinstance(value, Compartment):
            self._target = value.target
            return

        if isinstance(value, str):
            self._target = value

        raise ValueError("Invalid compartment target ", value)