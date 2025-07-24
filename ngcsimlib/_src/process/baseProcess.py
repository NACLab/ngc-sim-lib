from ngcsimlib._src.context.contextAwareObjectMeta import ContextAwareObjectMeta
from ngcsimlib._src.context.contextObjectDecorators import process
from ngcsimlib._src.global_state.manager import global_state_manager
from ngcsimlib._src.logger import warn, error
from ngcsimlib._src.utils.priority import priority
from ngcsimlib._src.parser.utils import compilable, _bind as bind
from ngcsimlib._src.compartment import Compartment

import ast

from typing import Union, TypeVar, Callable, List, Tuple, Dict
from numbers import Number
T = TypeVar('T')

@compilable
@priority(-1)
@process
class BaseProcess(metaclass=ContextAwareObjectMeta):
    def __init__(self, name):
        self.name = name
        self._keyword_order: List[str] = []
        self._watch_list: List[Compartment] = []

    def view_compiled_method(self) -> str:
        """
        Returns: The compiled method as a human-readable code block to assist
            with debugging.
        """
        if hasattr(self.run, "compiled"):
            return self.run.compiled.code
        return "Not Compiled"


    def watch(self, *compartments: Compartment):
        """
        Sets up the process to watch and return the values of specified
        compartments when run.

        Args:
            *compartments: positional arguments where each one is a Compartment
        """
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


    def _parse(self) -> Tuple[List, List, List, Dict]:
        raise NotImplemented

    def compile(self):
        bodies, extras, key_list, namespace = self._parse()

        self._keyword_order = key_list

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

        _compiled = ast.FunctionDef(
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

        if len(self._keyword_order) > 0:
            unpack = ast.Assign(targets=[
                ast.Tuple(
                    elts=[ast.Name(id=name, ctx=ast.Store()) for name in
                          self._keyword_order],
                    ctx=ast.Store()
                )
            ],
                value=ast.Name(id="loop_args", ctx=ast.Load())
            )

            _compiled.body[:0] = [unpack]
        _compiled = ast.Module(body=[_compiled], type_ignores=[])

        ast.fix_missing_locations(_compiled)

        bind(self,
             self.run,
             _compiled,
             namespace=namespace,
             auxiliary_ast=extras)