"""
This file contains the logic needed to compile down an operation and produce
an execution order that is compatible with the order found in the command
compiler.

This file contains two methods a parse and a compile method for operations.
The parse method returns the metadata needed by the command compiler to know
what values the operation will use.

The second one is the compile method which returns the execution order for
the compile operation. It is important to know that all operation should have
an `is_compilable` flag set to true if they are compilable. Some operations
such as the `add` operation are not compilable as their resolve method
contains execution logic that will not be captured by the compiled command.
"""
from ngcsimlib.operations.baseOp import BaseOp
from ngcsimlib.compartment import Compartment
from ngcsimlib.logger import critical


def parse(op):
    """
    parses the provided operation

    Args:
        op: the operation to parse

    Returns:
        the parsed operation
    """
    assert op.is_compilable, ("Trying to compile an operation that is flagged "
                              "as not compilable")
    if op.destination is not None and not Compartment.is_compartment(
        op.destination):
        critical(
            f"An operation that is being compiled has an invalid destination,"
            f" {op.destination}")

    inputs = []
    for s in op.sources:
        if isinstance(s, BaseOp):
            needed_inputs, dest = parse(s)
            if dest is not None:
                critical(
                    "An operation with a destination compartment is being "
                    "used as a source object for another "
                    "operation")
            for inp in needed_inputs:
                if inp not in inputs:
                    inputs.append(inp)
        else:
            if not Compartment.is_compartment(s):
                critical(
                    "An operation has source that is not a compartment or "
                    "instance of BaseOp")
            inputs.append(s.path)

    return inputs, op.destination.name if op.destination is not None else None


def compile(op):
    """
        compiles the operation down to its execution order

    Args:
        op: the operation to compile

    Returns:
        the execution order needed to run this operation compiled
    """
    exc_order = []
    ops = []

    for idx, s in enumerate(op.sources):
        if isinstance(s, BaseOp):
            exc_order.append(compile(s))
            ops.append(idx)

    output = op.destination.path if op.destination is not None else None

    iids = []
    for s in op.sources:
        if isinstance(s, BaseOp):
            pass
        else:
            iids.append(str(s.path))

    def _op_compiled(**kwargs):
        computed_values = [cmd(**kwargs) for cmd, _, _ in exc_order]
        compartment_args = [kwargs.get(narg) for narg in iids]

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
