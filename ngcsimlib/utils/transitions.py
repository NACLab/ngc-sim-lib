from ngcsimlib.logger import critical, debug

__component_transitions = {}
__transition_meta_data = {}


def get_transition(klass, transition_key, root=None):
    """
    A helper method for searching through the transition list
    """
    class_name = klass.__name__

    if class_name + "/" + transition_key not in __component_transitions.keys():
        parent_classes = klass.__bases__
        if len(parent_classes) == 0:
            return None, None

        transition = None
        for parent in parent_classes:
            transition, meta = get_transition(parent, transition_key,
                                            root=klass if root is None else root)
            if transition is not None:
                return transition, meta

        if transition is None and root is None:
            critical(class_name, "has no transition for", transition_key)
        if transition is None:
            return None, None

    if root is not None:
        debug(
            f"{root.__name__} is using the transition from {class_name} for "
            f"resolving key \"{transition_key}\"")
    return __component_transitions[class_name + "/" + transition_key], \
        __transition_meta_data[class_name + "/" + transition_key]


def add_component_transition(class_name, transition_key, data):
    """
    A helper function for adding component transitions
    """
    __component_transitions[class_name + "/" + transition_key] = data


def add_transition_meta(class_name, transition_key, data):
    """
    A helper function for adding component transition metadata
    """
    __transition_meta_data[class_name + "/" + transition_key] = data


def using_transition(**kwargs):
    """
    A decorator for linking transitions defined in other classes to this class.
    the keyword arguments are compile_key=class_to_inherit_transition_from. This
    will add the transition directly to the class and thus will get used before
    any transitions in parent classes.

    Args:
        **kwargs:  any number or compile_key=class_to_inherit_transition_from
    """

    def _klass_wrapper(cls):
        klass_name = cls.__name__
        for key, value in kwargs.items():
            transition, data = get_transition(value, key)
            add_component_transition(klass_name, key, transition)
            add_transition_meta(klass_name, key, data)
        return cls

    return _klass_wrapper
