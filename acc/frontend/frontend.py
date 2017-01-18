"""
This is the front end's API.
"""
from acc.frontend.util.util import compile_kernel_module
from acc.frontend.util.util import get_modules_from_stackframe
from acc.frontend.util.util import get_functions_from_stackframe
from acc.frontend.util.util import get_function_names_from_source
from acc.frontend.util.util import load_kernel_module
from acc.frontend.loop.visitor import loop_visitor
import ast
import asttokens
import os


def parallelize_for_loop(fname, source, stackframe, signature,
        back_end, *args, **kwargs):
    """
    Parallelizes a for loop.
    This is just a proof of concept function to show the idea.
    This will only parallelize the first for loop in the
    given function.
    """
    atok = asttokens.ASTTokens(source, parse=True)
    tree = atok.tree
    v = loop_visitor(atok)
    v.visit(tree)

    task_source = v.loop_code
    task_vars = v.loop_vars
    signature_vars = signature.parameters
    frame = stackframe[0] # In 3.5, this can be stackframe.frame
    module_vars = get_modules_from_stackframe(frame)
    func_names = get_function_names_from_source(source, fname)
    funcs = get_functions_from_stackframe(frame, func_names)

    new_source = back_end.for_loop(src=source, task_src=task_source,
            arg_vars=signature_vars, imports=module_vars,
            functions_srcs=funcs)
    fname = compile_kernel_module(new_source)
    mod = load_kernel_module(fname)
    return mod.execute(*args, **kwargs)




