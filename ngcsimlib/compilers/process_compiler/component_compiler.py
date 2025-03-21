from ngcsimlib.compilers.process_compiler.op_compiler import compile as op_compile
from ngcsimlib.compartment import Compartment
from ngcsimlib.compilers.utils import compose

def compile(transition_method):
    composition = None
    component = transition_method.__self__

    pure_fn = transition_method.f
    output = transition_method.output_compartments

    varnames = transition_method.fargs

    args = []
    compartments = []
    parameters = []

    for name in varnames:
        if name not in component.__dict__.keys():
            args.append(name)
        elif Compartment.is_compartment(component.__dict__[name]):
            compartments.append(name)
        else:
            parameters.append(name)

    for conn in component.connections:
        composition = compose(composition, op_compile(conn))

    arg_methods = []
    for a in args:
        arg_methods.append((a, lambda current_state, **kwargs: kwargs.get(a, None)))

    for p in parameters:
        arg_methods.append((p, lambda current_state, **kwargs: component.__dict__.get(p, None)))

    for c in compartments:
        arg_methods.append((c, lambda current_state, **kwargs: current_state.get(component.__dict__[c].path, None)))

    def compiled(current_state, **kwargs):
        kargvals = {key: m(current_state, **kwargs) for key, m in arg_methods}
        vals = pure_fn(**kargvals)
        if len(output) > 1:
            for v, o in zip(vals, output):
                current_state[component.__dict__[o].path] = v
        else:
            current_state[component.__dict__[output[0]].path] = vals
        return current_state

    composition = compose(composition, compiled)

    return composition
