from ngcsimlib.utils.compartment import Get_Compartment_Batch, Set_Compartment_Batch


def wrap_command(command):
    """
    Wraps the provided command to provide the state of all compartments as input
    and saves the returned state to all compartments after running. Designed to
    be used with compiled commands

    Args:
        command: the command to wrap

    Returns:
        the output of the command after it's been executed
    """

    def _wrapped(**kwargs):
        vals = command(Get_Compartment_Batch(), **kwargs)
        Set_Compartment_Batch(vals)
        return vals

    return _wrapped


def compose(current_composition, next_method):
    if current_composition is None:
        return next_method

    return lambda current_state, **kwargs: next_method(
        current_composition(current_state, **kwargs), **kwargs)
