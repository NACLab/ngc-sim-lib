from ngcsimlib.compilers.utils import compose
from ngcsimlib.compilers.process_compiler.component_compiler import compile as compile_component
from ngcsimlib.logger import warn
from functools import wraps
from ngcsimlib.utils import add_component_transition, add_transition_meta
from ngcsimlib.utils import get_current_context, infer_context, Set_Compartment_Batch

class Process(object):
    def __init__(self, name):
        self._method = None
        self._calls = []
        self.name = name
        self._needed_contexts = set([])

        cc = get_current_context()
        if cc is not None:
            cc.register_process(self)

    @staticmethod
    def make_process(process_spec):
        newProcess = Process(process_spec['name'])

        for x in process_spec['calls']:
            path = x['path']
            ctx = infer_context(path)
            component_name = path.split("/")[-1]
            newProcess >> getattr(ctx.get_components(component_name), x['key'])
        return newProcess

    @property
    def pure(self):
        return self._method

    def __rshift__(self, other):
        return self.transition(other)

    def transition(self, transition_call):
        self._calls.append({"path": transition_call.__self__.path, "key": transition_call.resolver_key})
        self._needed_contexts.add(infer_context(transition_call.__self__.path))
        new_step = compile_component(transition_call)
        self._method = compose(self._method, new_step)
        return self

    def execute(self, update_state=False, **kwargs):
        if self._method is None:
            warn("Attempting to execute a process with no transition steps")
            return
        state = self.pure(self.get_required_state(), **kwargs)
        if update_state:
            self.updated_modified_state(state)
        return state

    def as_obj(self):
        return {"name": self.name, "calls": self._calls}

    def get_required_state(self):
        compound_state = {}
        for context in self._needed_contexts:
            compound_state.update(context.get_current_state())
        return compound_state

    @classmethod
    def updated_modified_state(cls, modified_state):
        Set_Compartment_Batch(modified_state)


def transition(output_compartments):
    def _wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)


        class_name = ".".join(f.__qualname__.split('.')[:-1])
        resolver_key = f.__qualname__.split('.')[-1]


        inner.fargs = f.__func__.__code__.co_varnames[:f.__func__.__code__.co_argcount]
        inner.f = f
        inner.output_compartments = output_compartments

        inner.class_name = class_name
        inner.resolver_key = resolver_key

        add_component_transition(class_name, resolver_key,
                               (f, output_compartments))

        add_transition_meta(class_name, resolver_key,([], [], [], True))

        return inner
    return _wrapper