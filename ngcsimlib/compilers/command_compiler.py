"""
This is the file that contains the code to compile a given command on a model.

There are a few ways to compile the commands for a model, firstly if there is a command object already initialized
that has a valid compile key and a list of components the base method of `compile_command(command)` can be used to produce
the desired output. If no command object has been initialized then the `dynamic_compile(*components, compile_key=None)`
can be used to produce the desired output without the need to first go through a command object. The output of either
compile method will be the same.

The output produced by compiling a command will be two objects.

The first object produced by compiling a command is the compiled method itself. This method requires at least one
positional argument and then any number of additional arguments. The first argument that is provided to the compiled
method is a python dictionary that contains the state for all compartments this method will need to access,
as discerning this can be a challenge it is normal to just pass it all compartments present on your model. The
remaining list of arguments are all the run time arguments that the various compiled methods need to run properly.
The return value of this compiled method is the final state of all compartments after running through the compiled
command. Note here that the value on the compartments are not automatically updated and that will need to be done after.

The second object produced by compiling a command is the list of arguments that the compile command is expecting to
be passed in alongside the initial state of all the compartments. It is a good habit to get into printing this list
out after compiling as it can help catch typos present in the compiled methods that will not cause the compiling to
fail but will produce unknown behavior.

There is a wrapper method offered in this file we recommend using to assist with the design patterned required by the
compiled command. This is done with `wrap_command(command)`. This method will return another method that removes the
need for creating the initial state of the compartments and setting all the compartment values after running. Arguments
are still required to be passed in at run time.

"""
from ngcsimlib.compilers.component_compiler import parse as parse_component, compile as compile_component
from ngcsimlib.compilers.op_compiler import parse as parse_connection
from ngcsimlib.utils import Get_Compartment_Batch, Set_Compartment_Batch
from ngcsimlib.logger import critical

def _compile(compile_key, components):
    """
    This is the top level compile method for commands. Note this does not actually require you to compile a
    specific command object as it works purely off the compile key provided to the method.
    The general process that this takes to compile down everything, is by producing an execution order that knows which
    methods that are going to be called and where the results of the method are supposed to be stored.

    The execution order is as follows:

    For each component in the provided array of components;
    | compile it with the provided key
    | resolve the outputs of the compiled function

    Args:
        compile_key: The key that is being compiled (mapped to each function that has the @resolver decorator
                    above it)

        components: The list of components to compile for this function

    Returns:
        Produces the two objects described at the top of this file
    """
    assert compile_key is not None
    ## for each component, get compartments, get output compartments
    resolvers = {}
    for c_name, component in components.items():
        resolvers[c_name] = parse_component(component, compile_key)

    needed_args = []
    needed_comps = []

    for c_name, component in components.items():
        _, outs, args, params, comps = resolvers[c_name]
        for a in args:
            if a not in needed_args:
                needed_args.append(a)

        for connection in component.connections:
            inputs, _ = parse_connection(connection)
            ncs = [str(i) for i in inputs]
            for nc in ncs:
                if nc not in needed_comps:
                    needed_comps.append(nc)

        for comp in comps:
            path = str(component.__dict__[comp].path)
            if path not in needed_comps:
                needed_comps.append(path)

    exc_order = []
    for c_name, component in components.items():
        exc_order.extend(compile_component(component, resolvers[c_name]))

    def compiled(compartment_values, **kwargs):
        for n in needed_args:
            if n not in kwargs:
                critical(f"Missing keyword argument \"{n}\" in compiled function."
                         f"\tExpected keyword arguments {needed_args}")

        for exc, outs, name in exc_order:
            _comps = {key: compartment_values[key] for key in needed_comps}
            vals = exc(**kwargs, **_comps)
            if len(outs) == 1:
                compartment_values[outs[0]] = vals
            elif len(outs) > 1:
                for v, t in zip(vals, outs):
                    compartment_values[t] = v
        return compartment_values

    return compiled, needed_args


def compile_command(command):
    """
    Compiles a given command object to the spec described at the top of this file

    Args:
        command: the command object

    Returns:
        compiled_command, needed_arguments

    """
    return _compile(command.compile_key, command.components)


def dynamic_compile(*components, compile_key=None):
    """
    Dynamically compiles a command without the need of a command object to produce
    the spec described at the top of this file.

    Args:
        *components: a list of components to be compiled

        compile_key: the compile key specifying what to compile

    Returns:
        compiled_command, needed_arguments
    """
    if compile_key is None:
        critical("Can not compile a command without a compile key")
    return _compile(compile_key, {c.name: c for c in components})


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
