from ngcsimlib.operations import BaseOp


def parse(op):
    assert op.is_compilable
    inputs = []
    for s in op.sources:
        if isinstance(s, BaseOp):
            needed_inputs, dest = parse(s)
            assert dest is None
            for inp in needed_inputs:
                if inp not in inputs:
                    inputs.append(inp)
        else:
            inputs.append(s.path)

    return inputs, op.destination.name if op.destination is not None else None


def compile(op, arg_order):
    exc_order = []
    ops = []

    for idx, s in enumerate(op.sources):
        if isinstance(s, BaseOp):
            exc_order.append(compile(s, arg_order))
            ops.append(idx)

    output = op.destination.path if op.destination is not None else None

    iids = []
    for s in op.sources:
        if isinstance(s, BaseOp):
            pass
        else:
            iids.append(str(s.path))

    def _op_compiled(*args):
        computed_values = [cmd(*args) for cmd, _, _ in exc_order]
        compartment_args = [args[arg_order.index(narg)] for narg in iids]

        _val_loc = 0
        _arg_loc = 0

        _args = []
        for i in range(len(op.sources)):
            if i in ops:
                _args.append(computed_values[_val_loc])
                _val_loc += 1
            else:
                _args.append(compartment_args[_arg_loc])
                _arg_loc += 1

        return op.operation(*_args)
    return (_op_compiled, [str(output)], "op")

