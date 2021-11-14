# nbagile
> Making `nbdev` more Agile-Friendly


## Install

`pip install nbagile`

## Goals:

- [x] When exporting source code using `docments`, attach and format the docstring to Numpy format
- [ ] Export tests and throw them into a pytest-compatible file format
- [ ] Make documentation run on Sphynx
- [ ] Tests are exported to a `tests` folder, source code to a source code folder, and Markdown/Sphynx documentation to a `docs` folder
- [ ] Individual notebooks can then be recreated from these three items

## Current Capabilities


### Using the CLI

Replace `nbdev_` commands with `nbagile_` to use it's capabilities. 
**Currently Supported**:
- `nbagile_build_lib`: Exports code and converts it to black-style + NumPy docstrings
- `nbagile_diff_nbs`: A special version of `nbdev_diff_nbs` to support how nbagile works
- `nbagile_build_docs`: Builds the docs using [nbverbose](https://muellerzr.github.io/nbverbose)

### Exporting code from `docments` to NumPy

[docments](https://fastcore.fast.ai/docments) is a very efficient way of documenting the parameters for your code, and is akin to how javscript is documented. We utilize comment-blocks and typing to describe how parameters are utilized. For example, we have the following:

```python
def addition(
    a:int, # The first number to add
    b:(int,float), # The second number to add
) -> int: # The sum of a and b
    "Adds a and b"
    return a+b
```

But this is not the commonly accepted way of documenting our code, and as a whole looks quite ugly.

`nbagile` supports building your [nbdev](https://nbdev.fast.ai) built libraries to instead automatically convert this code into a more NumPy-styled documentation string and definition, with the added bonus of it mimicing the Black format:

```python
def addition(a,b):
    """Adds a and b
    
    Parameters
    ----------
    a : int
      The first number to add
    b : (int,float)
      The second number to add
      
    Returns
    ----------
    int
      The sum of a and b
    """
    return a+b
```

This works for functions, classes, as well as functions wrapped around decorators.


### Optional `__all__` for nbdev

If you are not a fan of nbdev's `__all__` format in each file, there is an additional setting you can add to your `settings.ini`: `use_all`.

If set to `False`, you won't get the `__all__` being generated in each python file
