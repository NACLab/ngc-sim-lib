from ngcsimlib.logger import warn


def deprecated(fn):
    def _wrapped(*args, **kwargs):
        warn(fn.__qualname__, "is deprecated")
        return fn(*args, **kwargs)
    return _wrapped


def deprecate_args(_rebind=True, **arg_list):
    def _deprecate_args(fn):
        def _wrapped(*args, **kwargs):
            for kwarg in list(kwargs.keys()):
                if kwarg in arg_list.keys():
                    new_kwarg = arg_list[kwarg]
                    if new_kwarg is None:
                        warn(f"The argument \"{kwarg}\" is deprecated for {fn.__qualname__}, and will no longer be supported")
                    else:
                        warn(f"The argument \"{kwarg}\" is deprecated for {fn.__qualname__}, use \"{new_kwarg}\" instead")

                    if _rebind:
                        if new_kwarg is not None:
                            kwargs[new_kwarg] = kwargs[kwarg]
                        del kwargs[kwarg]

            return fn(*args, **kwargs)
        return _wrapped
    return _deprecate_args
