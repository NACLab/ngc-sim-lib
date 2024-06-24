from ngcsimlib.logger import critical, debug

__component_resolvers = {}
__resolver_meta_data = {}


def get_resolver(klass, resolver_key, root=None):
    """
    A helper method for searching through the resolver list
    """
    class_name = klass.__name__

    if class_name + "/" + resolver_key not in __component_resolvers.keys():
        parent_classes = klass.__bases__
        if len(parent_classes) == 0:
            return None, None

        resolver = None
        for parent in parent_classes:
            resolver, meta = get_resolver(parent, resolver_key, root=klass if root is None else root)
            if resolver is not None:
                return resolver, meta

        if resolver is None and root is None:
            critical(class_name, "has no resolver for", resolver_key)
        if resolver is None:
            return None, None

    if root is not None:
        debug(f"{root.__name__} is using the resolver from {class_name} for resolving key \"{resolver_key}\"")
    return __component_resolvers[class_name + "/" + resolver_key], __resolver_meta_data[class_name + "/" + resolver_key]


def add_component_resolver(class_name, resolver_key, data):
    """
    A helper function for adding component resolvers
    """
    __component_resolvers[class_name + "/" + resolver_key] = data


def add_resolver_meta(class_name, resolver_key, data):
    """
    A helper function for adding component resolvers metadata
    """
    __resolver_meta_data[class_name + "/" + resolver_key] = data

def using_resolver(**kwargs):
    """
    A decorator for linking resolvers defined in other classes to this class.
    the keyword arguments are compile_key=class_to_inherit_resolver_from. This
    will add the resolver directly to the class and thus will get used before
    any resolvers in parent classes.

    Args:
        **kwargs:  any number or compile_key=class_to_inherit_resolver_from
    """
    def _klass_wrapper(cls):
        klass_name = cls.__name__
        for key, value in kwargs.items():
            resolver, data = get_resolver(value, key)
            add_component_resolver(klass_name, key, resolver)
            add_resolver_meta(klass_name, key, data)
        return cls
    return _klass_wrapper
