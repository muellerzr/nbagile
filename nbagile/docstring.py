# AUTOGENERATED! DO NOT EDIT! File to edit: 99_test.ipynb (unless otherwise specified).


from __future__ import annotations


__all__ = ['get_annotations', 'reformat_function', 'addition']

# Cell
import inspect
#nbdev_comment from __future__ import annotations
import fastcore.docments as dments

# Cell
def get_annotations(
    source:str # Source code of function or class
):
    "Extracts the type annotations from source code"
    parse = ast.parse(source)
    arg_annos = []
    for i,anno in enumerate(parse.body[0].args.args):
        if anno.annotation is not None:
            arg_annos.append(astunparse.unparse(anno.annotation).strip('\n'))
        else:
            arg_annos.append(anno.annotation)
        parse.body[0].args.args[i].annotation = None
    if parse.body[0].returns is not None:
        ret_anno = astunparse.unparse(parse.body[0].returns).strip('\n')
    else:
        ret_anno = None
    return arg_annos, ret_anno

# Cell
def _get_leading(o):
    return len(o) - len(o.lstrip(o[0])), o[0]

# Cell
def reformat_function(
    source:str, # Source code
):
    "Takes messy source code and refactors it into a readable PEP-8 standard style"
    docs = dments.docments(source)
    annos = get_annotations(source)
    parsed_source = ast.parse(source)
    for i in range(len(parsed_source.body[0].args.args)):
        parsed_source.body[0].args.args[i].annotation = None
    unparsed_source = astunparse.unparse(parsed_source).lstrip('\n').split('\n')
    function_definition = unparsed_source[0]
    function_innards = "\n".join(unparsed_source[2:])
    def _get_whitespace(): return whitespace_char*num_whitespace

    num_whitespace, whitespace_char = _get_leading(unparsed_source[2])
    docstring = f'\n{_get_whitespace()}"""\n'
    docstring += f'{_get_whitespace()}Parameters\n'
    docstring += f'{_get_whitespace()}----------\n'
    for i, param in enumerate(docs.keys()):
        if param != "return":
            docstring += f'{_get_whitespace()}{param} : {annos[i]}\n'
            docstring += f'{whitespace_char * (num_whitespace+2)}{docs[param]}\n'
        if (annos[-1] != inspect._empty) and ('return' in docs.keys()):
            docstring += f'{_get_whitespace()}Returns\n'
            docstring += f'{_get_whitespace()}-------\n'
            docstring += f'{_get_whitespace()}{annos[-1]}\n'
            docstring += f'{_get_whitespace()}{docs["return"]}\n'
    docstring += f'{_get_whitespace()}"""\n'
    return f'{function_definition}{docstring}{function_innards}'

# Cell
def addition(
    a:int, # The first number to add
    b:int, # The second number to add
) -> int: # The sum of a and b
    "Adds two numbers together"
    return a+b