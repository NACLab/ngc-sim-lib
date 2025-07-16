import ast
from ngcsimlib.global_state.manager import global_state_manager
from ngcsimlib.logger import warn

class ContextTransformer(ast.NodeTransformer):

    def __init__(self, obj):
        super().__init__()
        self.obj = obj
        self.current_args = set()
        self.needed_keys = set()

    def visit_Return(self, node):
        pass

    def visit_FunctionDef(self, node):
        self.current_args = {arg.arg for arg in node.args.args if arg.arg != "self"}

        node.args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="ctx")],  # single positional arg: ctx
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=ast.arg(arg="kwargs")  # **kwargs
        )

        new_decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == 'compilable':
                continue
            new_decorators.append(dec)
        node.decorator_list = new_decorators

        node.name = self.obj.name + "_" + node.name
        self.generic_visit(node)

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
            new_node = ast.copy_location(
                stateVal._to_ast(node, 'ctx'),
                node
            )
            self.needed_keys.add(stateVal.target)
            return ast.fix_missing_locations(new_node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.current_args:
            return ast.copy_location(
                ast.Subscript(
                    value=ast.Name(id="kwargs", ctx=ast.Load()),
                    slice=ast.Constant(value=node.id),
                    ctx=node.ctx
                ),
                node
            )
        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            return node.func.value
        return node

    def visit_Expr(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "set":
                target = call.func.value
                target.ctx = ast.Store()
                value = call.args[0]
                return ast.copy_location(ast.Assign(targets=[target], value=value), node)

        return node
