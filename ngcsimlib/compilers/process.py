from ngcsimlib.compilers.utils import compose
from ngcsimlib.compilers.process_compiler.component_compiler import compile as compile_component
from ngcsimlib.logger import warn
from functools import wraps
from ngcsimlib.utils import add_component_transition, add_transition_meta

class Process(object):
    def __init__(self):
        self._method = None

    @property
    def pure(self):
        return self._method

    def __rshift__(self, other):
        return self.transition(other)

    def transition(self, transition_call):
        new_step = compile_component(transition_call)
        self._method = compose(self._method, new_step)
        return self

    def execute(self, current_state, **kwargs):
        if self._method is None:
            warn("Attempting to execute a process with no transition steps")
            return
        return self.pure(current_state, **kwargs)


def transition(output_compartments):
    def _wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        inner.fargs = f.__func__.__code__.co_varnames[:f.__func__.__code__.co_argcount]
        inner.f = f
        inner.output_compartments = output_compartments

        class_name = ".".join(f.__qualname__.split('.')[:-1])
        resolver_key = f.__qualname__.split('.')[-1]

        add_component_transition(class_name, resolver_key,
                               (f, output_compartments))

        add_transition_meta(class_name, resolver_key,([], [], [], True))

        return inner
    return _wrapper