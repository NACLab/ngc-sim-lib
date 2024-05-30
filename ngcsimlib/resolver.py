from ngcsimlib.compartment import Compartment
from ngcsimlib.utils import add_component_resolver, add_resolver_meta


def resolver(pure_fn,
             output_compartments=None,
             args=None,
             parameters=None,
             compartments=None,
             expand_args=True
             ):
    if not (args is None and parameters is None and compartments is None):
        parse_varnames = False
        if args is None:
            args = []
        if parameters is None:
            parameters = []
        if compartments is None:
            compartments = []
    else:
        parse_varnames = True
        varnames = pure_fn.__func__.__code__.co_varnames[:pure_fn.__func__.__code__.co_argcount]

    if output_compartments is None:
        output_compartments = []

    def _resolver(fn):
        if len(output_compartments) == 0:
            for n in fn.__code__.co_varnames[1:fn.__code__.co_argcount]:
                output_compartments.append(n)

        class_name = ".".join(fn.__qualname__.split('.')[:-1])
        resolver_key = fn.__qualname__.split('.')[-1]

        add_component_resolver(class_name, resolver_key, (pure_fn, output_compartments))

        add_resolver_meta(class_name, resolver_key, (args, parameters, compartments, parse_varnames))

        def _wrapped(self=None, *_args, **_kwargs):
            comps = {}
            params = {}
            cargs = {}
            if parse_varnames:
                for n in varnames:
                    if n not in self.__dict__.keys():
                        cargs[n] = _kwargs.get(n)
                    elif Compartment.is_compartment(self.__dict__[n]):
                        comps[n] = self.__dict__[n].value
                    else:
                        params[n] = self.__dict__[n]
            else:
                comps = {key: self.__dict__[key].value for key in compartments}
                params = {key: self.__dict__[key] for key in parameters}
                cargs = {key: _kwargs.get(key) for key in args}

            vals = pure_fn(**cargs, **params, **comps)
            if expand_args and len(output_compartments) > 1:
                fn(self, *vals)
            else:
                fn(self, vals)

        return _wrapped

    return _resolver
