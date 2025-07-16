import ast

class KwargsTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.transformed_kwargs = set()


    def visit_Subscript(self, node):
        self.generic_visit(node)

        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "kwargs"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            self.transformed_kwargs.add(node.slice.value)
            return ast.Name(id=node.slice.value, ctx=ast.Load())

        return node