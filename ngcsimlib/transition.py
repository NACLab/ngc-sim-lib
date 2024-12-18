from ngcsimlib.logger import warn
from ngcsimlib.utils import add_component_transition, add_transition_meta

def add_transition(pure_fn, cls, output_compartments=None, transition_key=None):
    if output_compartments is None:
        warn(f"Transition {pure_fn.__qualname__.split('.')[-1]} has no output_compartments and thus does not do anything")

    key = pure_fn.__qualname__.split('.')[-1] if transition_key is None else transition_key

    class_name = cls.__qualname__
    add_component_transition(class_name, key,
                           (pure_fn, output_compartments))
    add_transition_meta(class_name, key,
                      (None, None, None, True))


def transition(pure_fn, output_compartments=None, transition_key=None):
    def _transition(cls):
        add_transition(pure_fn, cls, output_compartments, transition_key)
        return cls
    return _transition
