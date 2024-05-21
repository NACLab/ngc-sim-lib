from ngcsimlib.compilers.component_compiler import parse as parse_component, compile as compile_component
from ngcsimlib.compartment import Get_Compartment_Batch, Set_Compartment_Batch

def _compile(compile_key, components):
    assert compile_key is not None
    ## for each component, get compartments, get output compartments
    resolvers = {}
    for c_name, component in components.items():
        resolvers[c_name] = parse_component(component, compile_key)

    needed_args = []
    needed_comps = []

    for c_name, component in components.items():
        _, outs, args, params, comps = resolvers[c_name]
        for _, a in args:
            if a not in needed_args:
                needed_args.append(a)

        for connection in component.connections:
            inputs, outputs = connection.parse()
            ncs = [str(i) for i in inputs]
            for nc in ncs:
                if nc not in needed_comps:
                    needed_comps.append(nc)

        for _, comp in comps:
            uid = str(component.__dict__[comp]._uid)
            if uid not in needed_comps:
                needed_comps.append(uid)

    arg_order = needed_args + needed_comps
    exc_order = []
    for c_name, component in components.items():
        exc_order.extend(compile_component(component, resolvers[c_name], arg_order))

    def compiled(compartment_values, *cargs):
        for exc, outs, name in exc_order:
            _comps = [compartment_values[key] for key in needed_comps]
            vals = exc(*cargs, *_comps)
            if len(outs) == 1:
                compartment_values[outs[0]] = vals
            elif len(outs) > 1:
                for v, t in zip(vals, outs):
                    compartment_values[t] = v
        return compartment_values

    return compiled, needed_args



def compile(command):
    return _compile(command.compile_key, command.components)

def dynamic_compile(*components, compile_key=None):
    assert compile_key is not None
    return _compile(compile_key, {c.name: c for c in components})

def wrap_command(command):
    def _wrapped(*args):
        vals = command(*args, compartment_values=Get_Compartment_Batch())
        Set_Compartment_Batch(vals)
        return vals
    return _wrapped
