from ngcsimlib.operations.baseOp import BaseOp

def _make_lambda(s):
    return lambda current_state, **kwargs: current_state[s.path]

def compile(op):
    """
        compiles the operation down to its execution order

    Args:
        op: the operation to compile

    Returns:
        the execution order needed to run this operation compiled
    """
    arg_methods = []
    for s in op.sources:
        if isinstance(s, BaseOp):
            arg_methods.append(compile(s))
        else:
            arg_methods.append(_make_lambda(s))

    def compiled(current_state, **kwargs):
        argvals = [m(current_state, **kwargs) for m in arg_methods]
        val = op.operation(*argvals)
        if op.destination is not None:
            current_state[op.destination.path] = val
            return current_state
        else:
            return val

    return compiled