from __future__ import annotations

__all__ = ['get_annotations', 'apply', 'reformat_function', 'reformat_class', 'clean_file', 'nbagile_build_lib',
           'nbagile_build_docs', 'nbagile_diff_nbs']

import inspect, ast, astunparse
import fastcore.docments as dments
from collections import OrderedDict
from fastcore.basics import risinstance
from fastcore.dispatch import retain_type
from fastcore.xtras import is_listy
import re

def get_annotations(source:str):
    """Extracts the type annotations from source code

    Parameters
    ----------
    source : str
      Source code of function or class
    """
    parse = ast.parse(source)
    arg_annos = []
    for (i, anno) in enumerate(parse.body[0].args.args):
        if (anno.annotation is not None):
            arg_annos.append(astunparse.unparse(anno.annotation).strip('\n'))
        else:
            arg_annos.append(anno.annotation)
        parse.body[0].args.args[i].annotation = None
    if (parse.body[0].returns is not None):
        ret_anno = astunparse.unparse(parse.body[0].returns).strip('\n')
    else:
        ret_anno = None
    return (arg_annos, ret_anno)

_nl = '\n'
# We need a way to not have ast delete our newlines when compiled in a string

def _get_leading(o):
    """
    Parameters
    ----------
    o : any
    """
    return ((len(o) - len(o.lstrip(o[0]))), o[0])

def apply(func:callable, x:any, *args, **kwargs):
    """Apply `func` recursively to `x`, passing on args. Originally from fastai.torch_core

    Parameters
    ----------
    func : callable
      A callable function
    x : any
      Something to apply `func` on
    """
    if is_listy(x):
        return type(x)([apply(func, o, *args, **kwargs) for o in x])
    if isinstance(x, dict):
        return {k: apply(func, v, *args, **kwargs) for (k, v) in x.items()}
    res = func(x, *args, **kwargs)
    return (res if (x is None) else retain_type(res, x))

def reformat_function(source:str):
    """Takes messy source code and refactors it into a readable PEP-8 standard style

    Parameters
    ----------
    source : str
      Source code
    """
    docs = dments.docments(source)
    parsed_source = ast.parse(source)
    annos = get_annotations(source)
    parsed_source.body[0].returns = None
    body = parsed_source.body[0].body
    unparsed_source = astunparse.unparse(parsed_source).lstrip(_nl).split(_nl)
    has_decorator = (len(parsed_source.body[0].decorator_list) > 0)
    function_definition = ('\n'.join(unparsed_source[:2]) if has_decorator else unparsed_source[0])
    function_definition = function_definition.replace(': ', ':')

    def _extract_innards(is_str: bool):
        i = (2 if is_str else 1)
        return ('\n'.join(unparsed_source[(i + 1):]) if has_decorator else '\n'.join(unparsed_source[i:]))
    function_innards = _extract_innards(isinstance(body[0].value, ast.Str))

    def _get_whitespace():
        return (whitespace_char * num_whitespace)
    if (unparsed_source[2] != ''):
        (num_whitespace, whitespace_char) = _get_leading(unparsed_source[2])
    elif (len(unparsed_source) < 4):
        (num_whitespace, whitespace_char) = _get_leading(unparsed_source[1])
    else:
        (num_whitespace, whitespace_char) = _get_leading(unparsed_source[3])
    docstring = f'{_nl}{_get_whitespace()}"""'
    if isinstance(body[0].value, ast.Str):
        _quotes = ("'", '"')
        orig_docstring = astunparse.unparse(body[0]).lstrip(whitespace_char).replace(_quotes[0], '').replace(_quotes[1], '')
        orig_docstring = orig_docstring.split('\\n')

        def _inner(line, whitespace_char):
            diff = (len(line) - len(line.lstrip()))
            whitespace = ((whitespace_char * diff) if (diff > 0) else _get_whitespace())
            return f'{_nl}{whitespace}{line}'
        o = apply(_inner, orig_docstring, whitespace_char=whitespace_char)
        o[0] = orig_docstring[0].lstrip()
        docstring += '\n'.join(o)
    param_string = f'{_nl}{_get_whitespace()}Parameters{_nl}{_get_whitespace()}----------{_nl}'
    if (len(docs.keys()) >= 1):
        param_string = f'{_nl}{_get_whitespace()}Parameters{_nl}{_get_whitespace()}----------{_nl}'
        for (i, param) in enumerate(docs.keys()):
            if ((param != 'return') and (param != 'self') and (param != 'cls')):
                param_string += f'{_get_whitespace()}{param}'
                if (annos[0][i] is not None):
                    param_string += f' : {annos[0][i]}'
                else:
                    param_string += f' : any'
                param_string += '\n'
                if (docs[param] is not None):
                    param_string += f'{(whitespace_char * (num_whitespace + 2))}{docs[param]}{_nl}'
    if (param_string != f'{_nl}{_get_whitespace()}Parameters{_nl}{_get_whitespace()}----------{_nl}'):
        docstring += param_string
    if ((annos[(- 1)] != inspect._empty) and ('return' in docs.keys())):
        docstring += f'{_nl}{_get_whitespace()}Returns{_nl}'
        docstring += f'{_get_whitespace()}-------{_nl}'
        docstring += f'{_get_whitespace()}{annos[1]}{_nl}'
        docstring += f"{(whitespace_char * (num_whitespace + 2))}{docs['return']}{_nl}"
    docstring += f'{_get_whitespace()}"""{_nl}'
    return f'{function_definition}{docstring}{function_innards}'

def reformat_class(source:str, recursion_level:int=1):
    """Takes messy class code and refactors it into a readable PEP-8 standard style

    Parameters
    ----------
    source : str
      Source code of a full class
    recursion_level : int
      Depth of recursion
    """
    whitespace_char = None

    def _format_spacing(code, num_leading):
        code = [c for c in code if (len(c) > 0)]

        def _inner(c, num_leading):
            curr_leading = (len(c) - len(c.lstrip()))
            return f'{(c[0] * (curr_leading - num_leading))}{c.lstrip()}'
        return apply(_inner, code, num_leading=num_leading)
    parsed_source = ast.parse(source)
    body = parsed_source.body[0].body
    new_source = ''
    unparsed_source = astunparse.unparse(parsed_source).lstrip('\n').split('\n')
    new_source += unparsed_source[0]

    def _get_whitespace():
        return (whitespace_char * num_whitespace)
    (num_whitespace, whitespace_char) = _get_leading(unparsed_source[2])
    docstring = f'{_nl}{_get_whitespace()}"""'
    (docstring_len, diff) = (0, 2)
    new_nodes = [unparsed_source[0]]
    for (i, node) in enumerate(body):
        if risinstance((ast.ClassDef, ast.FunctionDef), node):
            beginning_lineno = node.lineno
            split_code = source.split('\n')
            if (i < (len(body) - 1)):
                ending_lineno = body[(i + 1)].lineno
                code = split_code[(beginning_lineno - 1):(ending_lineno - 1)]
                num_leading = (len(code[0]) - len(code[0].lstrip()))
                if isinstance(node, ast.ClassDef):
                    for (i, c) in enumerate(code):
                        code[i] = code[i][num_leading:]
                    new_nodes.append(reformat_class('\n'.join(code), (recursion_level + 1)))
                else:
                    if (whitespace_char is None):
                        whitespace_char = code[i][0]
                    code = _format_spacing(code, num_leading)
                    new_nodes.append(reformat_function('\n'.join(code)))
            else:
                code = split_code[(beginning_lineno - 1):]
                if (whitespace_char is None):
                    whitespace_char = code[i][0]
                num_leading = (len(code[0]) - len(code[0].lstrip()))
                code = _format_spacing(code, num_leading)
                new_nodes.append(reformat_function('\n'.join(code)))
        elif (isinstance(body[0].value, ast.Str) and (i == 0)):
            _quotes = ("'", '"')
            orig_docstring = astunparse.unparse(body[0]).lstrip(whitespace_char).replace(_quotes[0], '').replace(_quotes[1], '')
            orig_docstring = orig_docstring.split('\\n')

            def _inner(line, whitespace_char):
                diff = (len(line) - len(line.lstrip()))
                whitespace = ((whitespace_char * diff) if (diff > 0) else _get_whitespace())
                return f'{_nl}{whitespace}{line}'
            o = apply(_inner, orig_docstring, whitespace_char=whitespace_char)
            o[0] = orig_docstring[0].lstrip()
            docstring += '\n'.join(o)
            docstring += f'{_nl}{_get_whitespace()}"""'
            full_string = docstring.split('\n')
            new_string = ''
            if (len(full_string) == 4):
                new_string = apply((lambda x: x.lstrip()), full_string)
                new_string = ''.join(new_string)
            else:
                new_string = '\n'.join(full_string)
            docstring_len = len(new_string.split('\n'))
            new_nodes.append(new_string)
        else:
            new_nodes.append(f'{astunparse.unparse(node).strip()}')
    formatted_source = []
    num_chars = 4
    if (recursion_level > 1):
        num_chars += ((2 * (recursion_level - 1)) - 2)
    formatted_source.append(new_nodes[0])
    line = new_nodes[1]
    if (not (len(line.lstrip()) < len(line))):
        line = line.split('\n')
        line = apply((lambda x: f'{(whitespace_char * num_chars)}{x}'), line)
        line = '\n'.join(line)
    formatted_source.append(line.lstrip('\n'))
    for (i, line) in enumerate(new_nodes[2:]):
        l = line.split('\n')
        for (i, o) in enumerate(l):
            l[i] = f'{(whitespace_char * num_chars)}{o}'
        line = '\n'.join(l)
        formatted_source.append(line)
    return '\n'.join(formatted_source)

from fastcore.script import call_parse
from fastcore.xtras import Path

def clean_file(fname:(Path, str), use_all:bool):
    """Cleans an individual file from docment-style annotation to numpy-style

    Parameters
    ----------
    fname : (Path, str)
      The location of a filename to clean
    use_all : bool
      Whether to add a '__all__' to the file
    """
    if (not isinstance(fname, Path)):
        fname = Path(fname)
    if (not fname.exists()):
        raise ValueError(f'Warning! {fname} does not exist! Ensure you passed in a valid file location')
    contents = fname.read_text()
    new_funcs = []
    p = ast.parse(contents)
    (start_locs, end_locs, types) = ([], [], [])
    for (i, item) in enumerate(p.body):
        start_locs.append(item.lineno)
        if (i < (len(p.body) - 1)):
            end_locs.append((p.body[(i + 1)].lineno - 1))
        elif (i == (len(p.body) - 1)):
            end_locs.append((- 1))
        types.append(type(item))
    split_line = contents.split('\n')
    for (start, end) in zip(start_locs, end_locs):
        if (start == end):
            definition = '\n'.join([split_line[(start - 1)]])
        elif (end == (- 1)):
            definition = '\n'.join(split_line[(start - 1):])
        else:
            definition = '\n'.join(split_line[(start - 1):(end - 1)])
        new_funcs.append(definition)
    new_file_contents = ''
    for (i, (func, t)) in enumerate(zip(new_funcs, types)):
        if ((t == ast.Import) or (t == ast.ImportFrom)):
            if (i < (len(new_funcs) - 1)):
                new_file_contents += func
        elif (t == ast.ClassDef):
            try:
                new_file_contents += reformat_class(func)
            except:
                new_file_contents += func
        elif (t == ast.FunctionDef):
            try:
                o = reformat_function(func)
                if o.startswith('@'):
                    new_file_contents += f'{_nl}{o}'
                else:
                    new_file_contents += o
            except:
                new_file_contents += func
        elif (not func.endswith('\n')):
            new_file_contents += f'{func}{_nl}'
        else:
            new_file_contents += func
        new_file_contents += '\n'
    if (not use_all):
        new_file_contents = re.sub('^__all__\\s*=\\s*\\[([^\\]]*)\\]', '', new_file_contents, flags=re.MULTILINE)
    new_file_contents = new_file_contents.replace('\n# Cell\n', '')
    fname.write_text(new_file_contents)

import nbdev.export as exp
import nbdev.export2html as exp2html
from nbdev.imports import read_config_file

@call_parse
def nbagile_build_lib():
    """Export notebooks matching `fname` to python modules
    """
    exp2html.write_tmpls()
    exp.notebook2script()
    files = exp.nbglob(extension='.py', config_key='lib_path')
    cfg_path = Path.cwd()
    while ((cfg_path != cfg_path.parent) and (not (cfg_path / 'settings.ini').exists())):
        cfg_path = cfg_path.parent
    cfg = read_config_file((cfg_path / 'settings.ini'))
    for file in files:
        clean_file(file, use_all=cfg['use_all'])

from nbverbose.cli import nbdev_build_docs

@call_parse
def nbagile_build_docs():
    """Builds documentation from notebooks
    """
    exp2html.write_tmpls()
    exp.notebook2script()
    nbdev_build_docs()
    nbagile_build_lib()

import subprocess
from distutils.dir_util import copy_tree
import tempfile
import shutil

@call_parse
def nbagile_diff_nbs():
    """Prints the diff between an export of the library in notebooks and the actual modules
    """
    cfg = get_config()
    lib_folder = cfg.path('lib_path')
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        copy_tree(cfg.path('lib_path'), d1)
        exp.notebook2script(silent=True)
        files = exp.nbglob(extension='.py', config_key='lib_path')
        for file in files:
            clean_file(file)
        copy_tree(cfg.path('lib_path'), d2)
        shutil.rmtree(cfg.path('lib_path'))
        shutil.copytree(d1, str(cfg.path('lib_path')))
        for d in [d1, d2]:
            if (Path(d) / '__pycache__').exists():
                shutil.rmtree((Path(d) / '__pycache__'))
        res = subprocess.run(['diff', '-ru', d1, d2], stdout=subprocess.PIPE)
        print(res.stdout.decode('utf-8'))

