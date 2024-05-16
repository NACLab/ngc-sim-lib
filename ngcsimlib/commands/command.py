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
            pure_op, input_ids, output_id = connection.compile()
            iids = [str(i) for i in input_ids]

            def _op_compiled(*args):
                op_args = [args[arg_order.index(narg)] for narg in iids]
                return pure_op(*op_args)

            exc_order.append((_op_compiled, [str(output_id)], "op"))

        ### Component resolve
        comp_ids = [str(component.__dict__[comp]._uid) for comp in comps]
        out_ids = [str(component.__dict__[comp]._uid) for comp in outs]

        funParams = [component.__dict__[narg] for narg in (list(params))]

        def compiled(*args):
            funArgs = [args[arg_order.index(narg)] for narg in (list(_args))]
            funComps = [args[arg_order.index(narg)] for narg in comp_ids]
            # print(f"[DEBUG] funArgs: {funArgs}, funParams: {funParams}, funComps: {funComps}")
            return pure_fn(*funArgs, *funParams, *funComps)

        exc_order.append((compiled, out_ids, component.name))
        return exc_order


    def compile(self):
        assert self.compile_key is not None
        ## for each component, get compartments, get output compartments
        resolvers = {}
        for c_name, component in self.components.items():
            (pure_fn, output_compartments), (args, parameters, compartments) = \
                get_resolver(component.__class__.__name__, self.compile_key)

            if args is None:
                args = []
                parameters = []
                compartments = []
                varnames = pure_fn.__func__.__code__.co_varnames[:pure_fn.__func__.__code__.co_argcount]
                for n in varnames:
                    if n not in component.__dict__.keys():
                        args.append(n)
                    elif Compartment.is_compartment(component.__dict__[n]):
                        compartments.append(n)
                        # print(f"[DEBUG] added compartment: {n}")
                    else:
                        parameters.append(n)
                    # print(f"[DEBUG] n: {n}")

                if output_compartments is None:
                    output_compartments = compartments[:]

            resolvers[c_name] = (pure_fn, output_compartments, args, parameters, compartments)

        needed_args = []
        needed_comps = []
        init_comp_vals = {}
        for c_name, component in self.components.items():
            _, outs, args, params, comps = resolvers[c_name]
            for a in args:
                if a not in needed_args:
                    needed_args.append(a)

            for connection in component.connections:
                op, inputs, outputs = connection.compile()
                needed_comps.extend([str(i) for i in inputs])

            for comp in comps:
                needed_comps.append(str(component.__dict__[comp]._uid))
                init_comp_vals[str(component.__dict__[comp]._uid)] = component.__dict__[comp].value

        arg_order = needed_args + needed_comps
        exc_order = []
        for c_name, component in self.components.items():
            exc_order.extend(Command.__compile_component(component, resolvers[c_name], arg_order))

        def compiled(*cargs, compartment_values):
            for exc, outs, name in exc_order:
                _comps = [compartment_values[key] for key in needed_comps]
                # print(f"[DEBUG] params gen: {param_generator(i)}, cargs: {cargs}, needed_comps: {needed_comps}, _comps: {_comps}")
                vals = exc(*cargs, *_comps)
                if len(outs) == 1:
                    compartment_values[outs[0]] = vals
                elif len(outs) > 1:
                    for v, t in zip(vals, outs):
                        compartment_values[t] = v
            return {key: c for key, c in compartment_values.items()}

        return compiled, arg_order


