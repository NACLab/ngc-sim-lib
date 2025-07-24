import ast
from ngcsimlib._src.global_state.manager import global_state_manager
from ngcsimlib._src.logger import warn, error
from ngcsimlib._src.compartment.compartment import Compartment


class ContextTransformer(ast.NodeTransformer):
    """
    This transformer works to transpile a compilable method into a pure method.
    """
    def __init__(self, obj, method, subMethod=False):
        super().__init__()
        self.obj = obj
        self.method = method
        self.current_args = set()
        self.needed_keys = set()
        self.needed_methods = {}
        self.subMethod = subMethod
        self.needed_globals = {}

    def visit_Return(self, node):
        if self.subMethod:
            return self.generic_visit(node)
        return None

    def visit_FunctionDef(self, node):
        self.current_args = {arg.arg for arg in node.args.args if arg.arg != "self"}

        node.args = ast.arguments(
            posonlyargs=[],
            args=[arg if arg.arg != "self" else ast.arg(arg="ctx") for arg in node.args.args],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None
        )

        new_decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == 'priority':
                continue
            if isinstance(dec, ast.Name) and (dec.id == "staticmethod" or dec.id == "compilable"):
                continue
            new_decorators.append(dec)


        node.decorator_list = new_decorators

        node.name = self.obj.name + "_" + node.name
        self.generic_visit(node)

        if not self.subMethod:
            node.body.append(ast.Return(value=ast.Name(id='ctx', ctx=ast.Load())))
        self.current_args = set()


        for key in self.needed_keys:
            if not global_state_manager.check_key(key):
                warn(f"Key ({key}) missing from global state")

        return node

    def visit_Attribute(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            stateVal = getattr(self.obj, node.attr)
            if isinstance(stateVal, Compartment):
                new_node = ast.copy_location(
                    stateVal._to_ast(node, 'ctx'),
                    node
                )
                self.needed_keys.union(stateVal.get_needed_keys())

                return ast.fix_missing_locations(new_node)

            if callable(stateVal):
                method_name = f"{self.obj.name}_{node.attr}"
                new_node = ast.copy_location(ast.Name(id=method_name, ctx=node.ctx), node)
                self.needed_methods[method_name] = node.attr
                return ast.fix_missing_locations(new_node)

            attr_name = f"{self.obj.name}_{node.attr}"
            new_node = ast.copy_location(ast.Name(id=attr_name, ctx=node.ctx), node)
            self.needed_globals[attr_name] = stateVal
            return ast.fix_missing_locations(new_node)

        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            return node.func.value

        if isinstance(node.func, ast.Name) and node.func.id in self.needed_methods.keys():
            node.args = [ast.Name(id='ctx', ctx=ast.Load())] + node.args

        return node

    # def visit_Assign(self, node):
    #     for target in node.targets:
    #         if isinstance(target, ast.Name):
    #             target.id = f"{self.obj.name}_{target.id}"
    #             self.local_vars.add(target.id)
    #     return self.generic_visit(node)
    #
    #
    # def visit_Name(self, node):
    #     # if node.id in self.local_vars:
    #     #     node.id = f"{self.obj.name}_{node.id}"
    #     return node

    def visit_Expr(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "set":

                target = call.func.value
                target.ctx = ast.Store()
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == "ctx" and isinstance(target.slice, ast.Constant):
                    atr = target.slice.value.split(":")[-1]
                    val = getattr(self.obj, atr, None)
                    if val is not None and isinstance(val, Compartment):
                        if val.fixed:
                            error(f"Trying to compile "
                                  f"\"{self.method.__name__}\" "
                                  f"on {self.obj.name} and fixed compartment "
                                  f"{atr} is marked as fixed but has a set call")

                value = call.args[0]
                return ast.copy_location(ast.Assign(targets=[target], value=value), node)

        return node

    @staticmethod
    def _resolve_self_attr_chain_and_path(attr_node: ast.Attribute):
        """
        Returns (base_is_self, attr_chain: List[str])
        e.g., self.foo.targeted -> (True, ['foo', 'targeted'])
        """
        chain = []
        node = attr_node
        while isinstance(node, ast.Attribute):
            chain.insert(0, node.attr)
            node = node.value

        is_self = isinstance(node, ast.Name) and node.id == "self"
        return is_self, chain if is_self else None

    def visit_If(self, node):
        parent_map = {}
        for parent in ast.walk(node.test):
            for child in ast.iter_child_nodes(parent):
                parent_map[child] = parent

        for n in ast.walk(node.test):
            if isinstance(n, ast.Attribute):
                if isinstance(parent_map.get(n), ast.Attribute):
                    continue

                is_self, chain = self._resolve_self_attr_chain_and_path(n)
                if not is_self or not chain:
                    continue

                if chain[-1] == "targeted":
                    continue

                target = self.obj
                try:
                    for attr in chain:
                        target = getattr(target, attr)
                except AttributeError:
                    continue

                if isinstance(target, Compartment) and not target.fixed:
                    raise RuntimeError(f"{self.obj.name}:{self.method.__name__}:[{target.root}], Conditionals can not be dependant on model state")


        condition_expr = ast.Expression(node.test)
        compiled = compile(ast.fix_missing_locations(condition_expr), "<ast>", "eval")

        try:
            value = eval(compiled, {}, {"self": self.obj})
        except Exception as e:
            raise RuntimeError(f"On {self.obj.name}:{self.method.__name__} can not evaluate conditional\n{ast.unparse(node)}")

        case = (node.body if value else node.orelse)
        new_body = []
        for stmt in case:
            visited = self.visit(stmt)
            if isinstance(visited, list):
                new_body.extend(visited)
            else:
                new_body.append(visited)

        # Ensure each node has line/column metadata
        return [ast.fix_missing_locations(n) for n in new_body]
