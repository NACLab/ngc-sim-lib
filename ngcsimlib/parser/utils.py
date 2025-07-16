import inspect
import ast, textwrap
from .contextTransformer import ContextTransformer
from .kwargsTransformer import KwargsTransformer

def compilable(priority=None):
    def _compilable(fn):
        fn._is_compilable = True
        fn._priority = priority
        return fn
    return _compilable


def bind(obj, method, ast_obj, namespace=None):

    code = compile(ast_obj, filename=f"{method.__name__}_compiled", mode='exec')

    namespace = method.__globals__.copy() if namespace is None else namespace
    exec(code, namespace)

    method_text = ast.unparse(ast_obj)

    transformed_func = namespace[ast_obj.body[0].name]
    transformed_func.code = method_text
    transformed_func.ast = ast_obj
    transformed_func.namespace = namespace

    setattr(obj, method.__name__, _methodWrapper(method, transformed_func))


def convert_kwargs(tree: ast.AST):
    transformer = KwargsTransformer()
    transformed = transformer.visit(tree)
    ast.fix_missing_locations(transformed)
    return transformer.transformed_kwargs

def parse_method(obj, method):
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)
    transformed = ContextTransformer(obj).visit(tree)
    ast.fix_missing_locations(transformed)

    bind(obj, method, transformed)
    # method_text = ast.unparse(transformed)
    #
    # # # --- Compile and turn into a function object ---
    # # mod = ast.Module(body=[transformed_func], type_ignores=[])
    # code = compile(transformed, filename="<ast>", mode="exec")
    # #
    # # # Namespace to exec in
    # namespace = method.__globals__.copy()
    # exec(code, namespace)
    #
    # transformed_func = namespace[transformed.body[0].name]
    # transformed_func.code = method_text
    # transformed_func.ast = transformed
    #
    # setattr(obj, method.__name__, _methodWrapper(method, transformed_func))

def compileObject(obj):
    for name in dir(obj):
        attr = getattr(obj, name)
        if hasattr(attr, "_is_compilable") and not inspect.isclass(attr):
            parse_method(obj, attr)

class _methodWrapper:
    def __init__(self, bound_method, compiled):
        self._method = bound_method
        self.compiled = compiled

    def __call__(self, *args, **kwargs):
        return self._method(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self._method, attr)
