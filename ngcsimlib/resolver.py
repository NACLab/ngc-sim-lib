from ngcsimlib.compartment import Compartment

__component_resolvers = {}
__resolver_meta_data = {}

def get_resolver(class_name, resolver_key):
    return __component_resolvers[class_name + "/" + resolver_key], __resolver_meta_data[class_name + "/" + resolver_key]

def resolver(pure_fn,
             output_compartments=None,
             parse_varnames=True,
             args=None,
             parameters=None,
             compartments=None
             ):
    if parse_varnames is False:
        if args is None:
            args = []
        if parameters is None:
            parameters = []
        if compartments is None:
            compartments = []
        if output_compartments is None:
            output_compartments = compartments[:]
    else:
        varnames = pure_fn.__func__.__code__.co_varnames

    def _resolver(fn):

        class_name = ".".join(fn.__qualname__.split('.')[:-1])
        resolver_key = fn.__qualname__.split('.')[-1]

        __component_resolvers[class_name + "/" + resolver_key] = pure_fn, output_compartments

        __resolver_meta_data[class_name + "/" + resolver_key] = (args, parameters, compartments)

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
            fn(self, vals)
        return _wrapped
    return _resolver