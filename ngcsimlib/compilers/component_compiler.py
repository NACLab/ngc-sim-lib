"""
This is the file that contains the code to compile a component for a command.

There are two primary method provided in this file. The first of them is the parse command. This command is designed
to provide everything that is needed to compile the component down without actually doing so. This is generally used
by the command compiler to produce a working list of everything that is needed prior to the actual compiling of all
components.

The second method that is provided in this file the actual method for compiling the component. This method takes in
the component, the parsed component, and the global argument order for the compiled method. The result of this method
is the execution order needed to be run to compute the compiled method over this component. This execution order is
consistent with the same pattern used by the command compiler.

"""
from ngcsimlib.compilers.op_compiler import compile as op_compile
from ngcsimlib.utils import get_resolver
from ngcsimlib.compartment import Compartment


def parse(component, compile_key):
    """
    Returns the parsed version of a component for use in compiling

    Args:
        component: the component to parse

        compile_key: the key to parse with

    Returns: the pure function,
             the output compartments to resolve to,
             the arguments needed,
             the parameters needed,
             the compartments needed

    """
    (pure_fn, output_compartments), (args, parameters, compartments, parse_varnames) = \
        get_resolver(component.__class__.__name__, compile_key)

    if parse_varnames:
        args = []
        parameters = []
        compartments = []
        varnames = pure_fn.__func__.__code__.co_varnames[:pure_fn.__func__.__code__.co_argcount]

        for idx, n in enumerate(varnames):
            if n not in component.__dict__.keys():
                args.append((idx, n))
            elif Compartment.is_compartment(component.__dict__[n]):
                compartments.append((idx, n))
            else:
                parameters.append((idx, n))

        if output_compartments is None:
            output_compartments = compartments[:]

    return (pure_fn, output_compartments, args, parameters, compartments)


def compile(component, resolver):
    """
        compiles down the component to a single pure method

    Args:
        component: the component to compile

        resolver: the parsed output of the component

    Returns:
        the compiled method
    """
    exc_order = []
    pure_fn, outs, _args, params, comps = resolver

    ### Op resolve
    for connection in component.connections:
        exc_order.append(op_compile(connection))

    ### Component resolve
    comp_ids = [str(component.__dict__[comp].path) for _, comp in comps]
    out_ids = [str(component.__dict__[comp].path) for comp in outs]

    funParams = {narg: component.__dict__[narg] for _, narg in (list(params))}

    def compiled(**kwargs):
        funArgs = {narg: kwargs.get(narg) for _, narg in (list(_args))}
        funComps = {narg.split('/')[-1]: kwargs.get(narg) for narg in comp_ids}

        return pure_fn(**funParams, **funArgs, **funComps)

    exc_order.append((compiled, out_ids, component.name))
    return exc_order
