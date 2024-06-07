"""
The resolver is an important part of the compiling of components and commands in the ngcsimlib compilers.

At its core the resolver links a pure (static) method with a class method that knows how to process the output values
of the pure method and set the correct compartment's values from it.

While a resolver can take in many arguments generally this is not needed as it will automatically map all the values it
needs from argument lines. When writing the resolvers and the pure functions being passed into them the names of the
arguments are very important, this extends to the name of the method the resolver is wrapping as that is the name the
resolver is saved under. When the compiler is searching for how to compile the compile key for a given component it
searches through all the resolvers on the class for any wrapping a method with the same name as the compile key. On
top of serving as the compile key the wrapped function provides the knowledge of where output values of the compiled
function should go and should not contain any runtime logic as this wrapped method will not be called when the
command is compiled.

The parsing of output_compartments, args, parameters, and compartments is done during compiling the resolvers,
but it will be explained here.

To parse the output_compartments the resolver looks at the names and order of the arguments in the method it is
wrapping. When it is compiled these names are the names of the compartments the compiled method will try to locate to
place the resultant values in. It is important to note that the number of output values of the pure method and the
number of input values should match for automatic mapping.

To parse the args, parameters, and compartments the argument names of the pure method are considered. First the
compiler will check to see if the name exists as an attribute on the object. If it does not exist the compiler assume
that this value is an argument being passed in by the user. In the event that it is present on the object it checks
to see if it is an instance of a compartment. In the event that it is it will add it to the compartments list
otherwise it will add it to the parameter list.
"""

from ngcsimlib.compartment import Compartment
from ngcsimlib.utils import add_component_resolver, add_resolver_meta


def resolver(pure_fn,
             output_compartments=None,
             args=None,
             parameters=None,
             compartments=None,
             expand_args=True
             ):
    """
    The decorator used to tell the ngcsimlib compiler how to compile methods on components.

    Args:
        pure_fn: the pure function where the run time logic is located

        output_compartments: a list of output compartment names (default: None)

        args: a list of arguments being passed into the pure function (default: None)

        parameters: a list of parameters being passed into the pure function (default: None)

        compartments: a list of compartments being passed into the pure function (default: None)

        expand_args: should the output of the pure method be expanded or kept as a tuple when being passed into the
                    wrapped method. (default: True)

    Returns:
        A wrapped method that will pass the output of the pure function into the resolve when called.

    """
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

            vals = pure_fn.__func__(**cargs, **params, **comps)
            if expand_args and len(output_compartments) > 1:
                fn(self, *vals)
            else:
                fn(self, vals)

        return _wrapped

    return _resolver
