import operator
import types

def _unwrap(x):
    while hasattr(x, "_get_value"):
        x = x._get_value()
    return x


_BINARY_OPS = {
    '__add__': operator.add,
    '__sub__': operator.sub,
    '__mul__': operator.mul,
    '__matmul__': operator.matmul,
    '__truediv__': operator.truediv,
    '__floordiv__': operator.floordiv,
    '__mod__': operator.mod,
    '__pow__': operator.pow,
    '__lshift__': operator.lshift,
    '__rshift__': operator.rshift,
    '__and__': operator.and_,
    '__xor__': operator.xor,
    '__or__': operator.or_,
    '__eq__': operator.eq,
    '__ne__': operator.ne,
    '__lt__': operator.lt,
    '__le__': operator.le,
    '__gt__': operator.gt,
    '__ge__': operator.ge,
}

_REVERSE_OPS = {f"__r{name[2:]}__": op for name, op in _BINARY_OPS.items()}

class CompartmentMeta(type):
    def __new__(mcs, name, bases, namespace):
        def make_op(opfunc):
            def method(self, other):
                return opfunc(_unwrap(self), _unwrap(other))
            return method

        for dunder_name, opfunc in _BINARY_OPS.items():
            if dunder_name not in namespace:
                namespace[dunder_name] = make_op(opfunc)

        for dunder_name, opfunc in _REVERSE_OPS.items():
            if dunder_name not in namespace:
                namespace[dunder_name] = make_op(opfunc)

        return super().__new__(mcs, name, bases, namespace)