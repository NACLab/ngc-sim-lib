from abc import ABC, abstractmethod
from ngcsimlib.utils import check_attributes
from ngcsimlib.compartment import Compartment
from ngcsimlib.resolver import get_resolver


class Command(ABC):
    """
    The base class for all commands found in ngcsimlib. At its core, a command is
    essentially a method to be called by the controller that affects the
    components in a simulated complex system / model in some way. When a command
    is made, a preprocessing step is run to verify that all of the needed
    attributes are present on each component. Note that this step does not
    ensure types or values, just that they do or do not exist.
    """

    """
    The Compile key is the name of the resolver the compile function will look for
    when compiling this command. If unset the compile will fail.
    """
    compile_key = None

    def __init__(self, components=None, command_name=None, required_calls=None):
        """
        Required calls on Components: ['name']

        Args:
            components: a list of components to run the command on

            required_calls: a list of required attributes for all components

            command_name: the name of the command on the controller
        """
        self.name = str(command_name)
        self.components = {}
        required_calls = ['name'] if required_calls is None else required_calls + ['name']
        for comp in components:
            if check_attributes(comp, required_calls, fatal=True):
                self.components[comp.name] = comp

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @staticmethod
    def __compile_component(component, resolver, arg_order):
        exc_order = []
        pure_fn, outs, _args, params, comps = resolver

        ### Op resolve
        for connection in component.connections:
            exc_order.append(connection.compile(arg_order))

        ### Component resolve
        comp_ids = [str(component.__dict__[comp]._uid) for _, comp in comps]
        out_ids = [str(component.__dict__[comp]._uid) for comp in outs]

        funParams = [component.__dict__[narg] for _, narg in (list(params))]

        arg_locs = [loc for loc, _ in _args]
        param_locs = [loc for loc, _ in params]
        comp_locs = [loc for loc, _ in comps]


        def compiled(*args):
            funArgs = [args[arg_order.index(narg)] for _, narg in (list(_args))]
            funComps = [args[arg_order.index(narg)] for narg in comp_ids]

            fargs = []
            for i in range(len(arg_locs) + len(param_locs) + len(comp_locs)):
                if i in arg_locs:
                    fargs.append(funArgs.pop(0))
                elif i in param_locs:
                    fargs.append(funParams.pop(0))
                else:
                    fargs.append(funComps.pop(0))

            return pure_fn(*fargs)

        exc_order.append((compiled, out_ids, component.name))
        return exc_order


    def compile(self):
        assert self.compile_key is not None
        ## for each component, get compartments, get output compartments
        resolvers = {}
        for c_name, component in self.components.items():
            (pure_fn, output_compartments), (args, parameters, compartments, parse_varnames) = \
                get_resolver(component.__class__.__name__, self.compile_key)


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



            resolvers[c_name] = (pure_fn, output_compartments, args, parameters, compartments)

        needed_args = []
        needed_comps = []

        for c_name, component in self.components.items():
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
        for c_name, component in self.components.items():
            exc_order.extend(Command.__compile_component(component, resolvers[c_name], arg_order))

        def compiled(*cargs, compartment_values):
            for exc, outs, name in exc_order:
                _comps = [compartment_values[key] for key in needed_comps]
                vals = exc(*cargs, *_comps)
                if len(outs) == 1:
                    compartment_values[outs[0]] = vals
                elif len(outs) > 1:
                    for v, t in zip(vals, outs):
                        compartment_values[t] = v
            return compartment_values

        return compiled, arg_order


