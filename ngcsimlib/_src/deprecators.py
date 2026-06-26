from ngcsimlib._src.logger import warn


def deprecated(replaced_by=None): ## function deprecating decorator
    def decorator(fn):
        def _wrapped(*args, **kwargs):
            message = "is deprecated" ## <= default warning message
            if replaced_by: ## make known substitute function name, if replaced_by != None
                ## uses __name__ or string representation
                new_name = getattr(replaced_by, '__name__', str(replaced_by))
                message += f" (use {new_name} instead)"
            warn(fn.__qualname__, message)
            return fn(*args, **kwargs)
        _wrapped._is_deprecated = True
        _wrapped._original = fn 
        return _wrapped
    return decorator


def deprecate_args(_rebind=True, **arg_list): ## argument deprecating decorator
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

        _wrapped._is_deprecated = True
        _wrapped._original = fn
        return _wrapped
    return _deprecate_args
