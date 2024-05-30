from ngcsimlib.compilers.op_compiler import compile as op_compile

from ngcsimlib.utils import get_resolver
from ngcsimlib.compartment import Compartment


def parse(component, compile_key):
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


def compile(component, resolver, arg_order):
    exc_order = []
    pure_fn, outs, _args, params, comps = resolver

    ### Op resolve
    for connection in component.connections:
        exc_order.append(op_compile(connection, arg_order))

    ### Component resolve
    comp_ids = [str(component.__dict__[comp].path) for _, comp in comps]
    out_ids = [str(component.__dict__[comp].path) for comp in outs]

    funParams = [component.__dict__[narg] for _, narg in (list(params))]

    arg_locs = [loc for loc, _ in _args]
    param_locs = [loc for loc, _ in params]
    comp_locs = [loc for loc, _ in comps]

    def compiled(*args):
        funArgs = [args[arg_order.index(narg)] for _, narg in (list(_args))]
        funComps = [args[arg_order.index(narg)] for narg in comp_ids]

        _arg_loc = 0
        _param_loc = 0
        _comps_loc = 0

        fargs = []
        for i in range(len(arg_locs) + len(param_locs) + len(comp_locs)):
            if i in arg_locs:
                fargs.append(funArgs[_arg_loc])
                _arg_loc += 1
            elif i in param_locs:
                fargs.append(funParams[_param_loc])
                _param_loc += 1
            else:
                fargs.append(funComps[_comps_loc])
                _comps_loc += 1

        return pure_fn(*fargs)

    exc_order.append((compiled, out_ids, component.name))
    return exc_order
