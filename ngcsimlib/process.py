from ngcsimlib.parser.utils import compilable, convert_kwargs, bind
from ngcsimlib.global_state.manager import global_state_manager
from ngcsimlib.context.contextObjectMeta import ContextObjectMeta
from ngcsimlib.logger import error, warn

import ast
from typing import Union, Callable, TypeVar, List
from numbers import Number

T = TypeVar('T')

@compilable(priority=-1)
class Process(metaclass=ContextObjectMeta):
    _type = "process"

    def __init__(self, name):
        self.name = name
        self.method_order = []
        self._compiled = None
        self._keyword_order = []

    def view_compiled_method(self) -> str:
        if hasattr(self.run, "compiled"):
            return self.run.compiled.code
        return "Not Compiled"

    def then(self, method):
        self.method_order.append((method.__self__, method.__name__))
        return self

    def get_keywords(self):
        return self._keyword_order

    def pack_keywords(self, row_seed: Union[T, None] = None, **kwargs: Union[Number, Callable[[T], Number]]) -> List[Number]:
        for key in self._keyword_order:
            if key not in kwargs:
                error(f"Key {key} is required to pack the arguments for process {self.name}")

        row = []
        for key in self._keyword_order:
            val = kwargs[key]
            if callable(val):
                if row_seed is None:
                    error(f"Making an unseeded row but encountered a keyword ({key}) that has a generator and needs a seed")
                row.append(val(row_seed))
            else:
                row.append(val)
        return row

    def pack_rows(self, length: int,
                  seed_generator: Union[Callable[[Number], T], None] = None,
                  **kwargs: Union[Number, Callable[[T], Number]]) -> List[List[Number]]:

        if seed_generator is None:
            seed_generator = lambda x: x
        return [self.pack_keywords(seed_generator(i), **kwargs) for i in range(length)]

    def compile(self):
        bodies = []
        for obj, method in self.method_order:
            obj_ast = getattr(obj, method).compiled.ast
            if not isinstance(obj_ast, ast.Module):
                continue

            body = obj_ast.body[0].body[:-1]
            bodies.extend(body)

        bodies.append(ast.Return(value=ast.Tuple(
                                elts=[
                                    ast.Name(id='ctx', ctx=ast.Load()),
                                    ast.Constant(value=None)
                                ], ctx=ast.Load())))

        self._compiled = ast.FunctionDef(
            name=self.name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='ctx'), ast.arg(arg='loop_args')],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=bodies,
            decorator_list=[],
        )

        self._keyword_order = convert_kwargs(self._compiled)
        if len(self._keyword_order) > 0:
            unpack = ast.Assign(targets=[
                ast.Tuple(
                    elts=[ast.Name(id=name, ctx=ast.Store()) for name in self._keyword_order],
                    ctx=ast.Store()
                )
            ],
            value=ast.Name(id="loop_args", ctx=ast.Load())
            )

            self._compiled.body[:0] = [unpack]
        self._compiled = ast.Module(body=[self._compiled], type_ignores=[])

        ast.fix_missing_locations(self._compiled)

        bind(self, self.run, self._compiled, namespace={k: v for obj, method_name in self.method_order for k, v in getattr(obj, method_name).compiled.namespace.items()})


    def run(self, state=None, keywords=None, update=True, row_seed=None, **kwargs):
        if hasattr(self.run, "compiled"):
            if state is None:
                state = global_state_manager.state
            if keywords is None:
                keywords = self.pack_keywords(row_seed=row_seed, **kwargs)
            final_state = self.run.compiled(state, keywords)
            if update:
                global_state_manager.set_state(final_state)
            return final_state
        else:
            warn("Trying to run a process while it is not compiled. Make sure "
                 "that the context that the process was created in has been "
                 "closed before trying to run the method.")
