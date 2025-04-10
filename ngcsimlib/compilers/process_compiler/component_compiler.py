"""
This file contains the methods used to compile methods for the use of Processes.
The general methodology behind this compiler is that if all transitions can be
expressed as f(current_state, **kwargs) -> final_state they can then be composed
together as f(g(current_state, **kwargs) **kwargs) -> final_state. While it is
technically possible to use the compiler outside the process its intended use
case is through the process and thus if error occur though other uses support
may be minimal.
"""

from ngcsimlib.compilers.process_compiler.op_compiler import compile as op_compile
from ngcsimlib.compartment import Compartment
from ngcsimlib.compilers.utils import compose

def __make_get_arg(a):
    return lambda current_state, **kwargs: kwargs.get(a, None)

def __make_get_param(p, component):
    return lambda current_state, **kwargs: component.__dict__.get(p, None)

def __make_get_comp(c, component):
    return lambda current_state, **kwargs: current_state.get(component.__dict__[c].path, None)

def _builder(transition_method_to_build):
    component = transition_method_to_build.__self__
    builder_method = transition_method_to_build.f
    # method, output_compartments, args, params, input_compartments
    return builder_method(component)


def compile(transition_method):
    """
    This method is the main compile method for the process compiler. Unlike the
    legacy compiler this compiler is designed to be self-contained and output
    the methods that are composed together to make the process compiler function
    Args:
        transition_method: a method usually component.method that has been
        decorated by the @transition decorator.

    Returns: the pure compiled method of the form
    f(current_state, **kwargs) -> final_state)

    """
    composition = None
    component = transition_method.__self__

    if transition_method.builder:
        pure_fn, output, args, parameters, compartments = _builder(transition_method)
    else:

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
    needed_args = []
    for a in args:
        needed_args.append(a)
        arg_methods.append((a, __make_get_arg(a)))

    for p in parameters:
        arg_methods.append((p, __make_get_param(p, component)))

    for c in compartments:
        arg_methods.append((c, __make_get_comp(c, component)))

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

    return composition, needed_args
