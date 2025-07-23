from ngcsimlib._src.parser.utils import compilable, convert_kwargs, _bind as bind, CompiledMethod
from ngcsimlib._src.global_state.manager import global_state_manager
from ngcsimlib._src.context.context_manager import global_context_manager
from ngcsimlib._src.context.contextObjectDecorators import process
from ngcsimlib._src.context.contextAwareObjectMeta import ContextAwareObjectMeta
from ngcsimlib._src.logger import error, warn
from ngcsimlib._src.utils.priority import priority
from ngcsimlib._src.compartment import Compartment

import ast
from typing import Union, Callable, TypeVar, List, Dict, Any
from numbers import Number

T = TypeVar('T')

@compilable
@priority(-1)
@process
class Process(metaclass=ContextAwareObjectMeta):
    """
    The process in ngcsimlib is the tool used to compile together a set of
    components and methods. As a context aware object processes hook into the
    compile step of all context aware objects but have the priority of -1, so
    they should always compile after all components have been compiled.

    Building a process follows a chain-like process. After initializing the
    process it is possible to chain `.then` calls one after another to build the
    steps of the process (this is can also be accomplished with `>>`). After
    all the steps of the process are set, nothing happens until it is time to
    compile the process.

    Compiling the process goes through and extracts the body of each compiled
    method in its order and pieces them together into a single large method
    call. The resulting method is a pure function that takes in state and
    loop_args returns the updated state.

    To make use of this compiled process simply invoke `.run` and it will use
    the compiled method. If just the compiled method itself is needed calling
    `.run.compiled` will provide direct access.
    """
    _type = "process"

    def __init__(self, name):
        self.name = name
        self.method_order = []
        self._compiled = None
        self._keyword_order = []
        self._watch_list = []

    def view_compiled_method(self) -> str:
        """
        Returns: The compiled method as a human-readable code block to assist
            with debugging.
        """
        if hasattr(self.run, "compiled"):
            return self.run.compiled.code
        return "Not Compiled"

    def then(self, method):
        """
        Used to specify the order of operations inside the process.
        Args:
            method: The compilable method to run next in the process sequence

        Returns: this process for easy chaining
        """
        self.method_order.append((method.__self__, method.__name__))
        return self

    def __rshift__(self, method):
        return self.then(method)

    def watch(self, *compartments: Compartment):
        self._watch_list.extend(compartments)

    def get_keywords(self):
        """
        Returns: The order that the compiled process expects keywords to be
            packed in. Mostly used for debugging.
        """
        return self._keyword_order

    def pack_keywords(self, row_seed: Union[T, None] = None, **kwargs: Union[Number, Callable[[T], Number]]) -> List[Number]:
        """
        This method will pack a specific iteration of the process's keywords
        into a list to be passed into its `.run` method. Each iteration has a
        seed that is needed so it can be passed into the generators used to
        produce the keyword arguments.

        Args:
            row_seed: the seed to be passed to the generators, can be none if no
                keywords are generators
            **kwargs: Either the constant value or lambda expression for
                producing keyword arguments based on a given seed.

        Returns: A single slice of keywords in the order the process expects
            them.

        """
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
        """
        Packs multiple rows of keywords together for easy of iteration.

        Args:
            length: The number of rows of keywords to pack
            seed_generator: A generator to produce the seeds for the rows, if
                no generator is provided the row index will be used as the seed.
            **kwargs:  Either the constant value or lambda expression for
                producing keyword arguments based on a given seed.

        Returns: a list of rows of keywords in the order the process expects

        """
        if seed_generator is None:
            seed_generator = lambda x: x
        return [self.pack_keywords(seed_generator(i), **kwargs) for i in range(length)]

    def compile(self):
        """
        Compiles the process. This needs to be called after each component that
        is used in the process is compiled, or it will not be able to find the
        metadata it is looking for.
        """
        bodies = []
        extras = []
        key_set = set()
        for obj, method in self.method_order:
            m: CompiledMethod = getattr(obj, method).compiled
            obj_ast = m.ast
            if not isinstance(obj_ast, ast.Module):
                continue

            for arg in obj_ast.body[0].args.args:
                if arg.arg != "ctx":
                    key_set.add(arg.arg)


            body = obj_ast.body[0].body[:-1]
            bodies.extend(body)

            extras.extend(m.auxiliary_ast)
            # print(method, m.namespace)

        self._keyword_order = list(key_set)


        watched = ast.Constant(value=None)
        if len(self._watch_list) > 0:
            watched = ast.Tuple(
                    elts=[
                        ast.Subscript(
                            value=ast.Name(id='ctx', ctx=ast.Load()),
                            slice=ast.Constant(value=compartment.target),
                            ctx=ast.Load()
                        )
                        for compartment in self._watch_list
                    ],
                    ctx=ast.Load()
                )


        bodies.append(ast.Return(value=ast.Tuple(
                                elts=[
                                    ast.Name(id='ctx', ctx=ast.Load()),
                                    watched
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

        print(self._keyword_order)
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

        bind(self,
             self.run,
             self._compiled,
             namespace={k: v for obj, method_name in self.method_order for k, v in getattr(obj, method_name).compiled.namespace.items()},
             auxiliary_ast=extras)



    def run(self, state=None, keywords=None, update=True, row_seed=None, **kwargs):
        """
        Runs the compiled process.

        Args:
            state: the initial state to use, if None it will default to the
                current global state.
            keywords: the packed keywords to use, if None it will default to
                using the kwargs and packing them based on the row seed
            update: should the global state be updated after the process is
                finished running.
            row_seed: if no keywords are provided it will pass this value when
                packing the keywords.

            **kwargs: If keywords are not prepacked, either a constant value or
                lambda expression for producing keyword arguments based on a
                given seed.

        Returns: The final state, watched values as a tuple

        """
        if hasattr(self.run, "compiled"):
            if state is None:
                state = global_state_manager.state
            if keywords is None:
                keywords = self.pack_keywords(row_seed=row_seed, **kwargs)
            final_state, other = self.run.compiled(state, keywords)
            if update:
                global_state_manager.set_state(final_state)
            return final_state, other
        else:
            warn("Trying to run a process while it is not compiled. Make sure "
                 "that the context that the process was created in has been "
                 "closed before trying to run the method.")


    def to_json(self) -> Dict[str, Any]:
        """
        This method returns dictionary of data to be saved in the json file that
        will be used to rebuild this object.

        Returns: A dictionary of data that can be serialized by JSON.
        """
        data = {"args": [self.name],
                "kwargs": {},
                "method_order": [
                        {"name": obj.name, "method": method} for obj, method in self.method_order
                    ],
                "watch_list": [
                    compartment.root for compartment in self._watch_list
                ]

                }
        return data

    def from_json(self, data: Dict[str, Any]) -> None:
        method_order = data.get("method_order", [])
        ctx = global_context_manager.current_context
        for step in method_order:
            comp = ctx.get_components(step['name'])
            if comp is not None and hasattr(comp, step['method']):
                self.then(getattr(comp, step['method']))

        watch_list = data.get("watch_list", [])
        for compartment_root in watch_list:
            self.watch(global_state_manager.get_compartment(compartment_root))