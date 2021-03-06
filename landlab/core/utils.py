#! /usr/bin/env python
"""Some utilities for the landlab package."""

import numpy as np


SIZEOF_INT = np.dtype(np.int).itemsize


def as_id_array(array):
    """Convert an array to an array of ids.

    Parameters
    ----------
    array : ndarray
        Array of IDs.

    Returns
    -------
    ndarray
        A, possibly new, array of IDs.

    Examples
    --------
    >>> import numpy as np
    >>> from landlab.core.utils import as_id_array
    >>> x = np.arange(5)
    >>> y = as_id_array(x)
    >>> y
    array([0, 1, 2, 3, 4])

    >>> x = np.arange(5, dtype=np.int)
    >>> y = as_id_array(x)
    >>> y
    array([0, 1, 2, 3, 4])

    >>> x = np.arange(5, dtype=np.int32)
    >>> y = as_id_array(x)
    >>> y
    array([0, 1, 2, 3, 4])
    >>> y.dtype == np.int
    True

    >>> x = np.arange(5, dtype=np.int64)
    >>> y = as_id_array(x)
    >>> y
    array([0, 1, 2, 3, 4])
    >>> y.dtype == np.int
    True

    >>> x = np.arange(5, dtype=np.intp)
    >>> y = as_id_array(x)
    >>> y
    array([0, 1, 2, 3, 4])
    >>> y.dtype == np.int
    True
    """
    if array.dtype == np.int:
        return array.view(np.int)
    else:
        return array.astype(np.int)


if np.dtype(np.intp) == np.int:
    def _as_id_array(array):
        if array.dtype == np.intp or array.dtype == np.int:
            return array.view(np.int)
        else:
            return array.astype(np.int)
else:
    def _as_id_array(array):
        if array.dtype == np.int:
            return array.view(np.int)
        else:
            return array.astype(np.int)


def make_optional_arg_into_id_array(number_of_elements, *args):
    """Transform an optional argument into an array of element ids.

    Many landlab functions an optional argument of element ids that tells the
    function to operate only on the elements provided. However, if the argument
    is absent, all of the elements are to be operated on. This is a convenience
    function that converts such an arguments list into an array of elements
    ids.

    Parameters
    ----------
    number_of_elements : int
        Number of elements in the grid.
    array : array_like
        Iterable to convert to an array.

    Returns
    -------
    ndarray
        Input array converted to a numpy array, or a newly-created numpy
        array.

    Examples
    --------
    >>> import numpy as np
    >>> from landlab.core.utils import make_optional_arg_into_id_array
    >>> make_optional_arg_into_id_array(4)
    array([0, 1, 2, 3])
    >>> make_optional_arg_into_id_array(4, [0, 0, 0, 0])
    array([0, 0, 0, 0])
    >>> make_optional_arg_into_id_array(4, (1, 1, 1, 1))
    array([1, 1, 1, 1])
    >>> make_optional_arg_into_id_array(4, np.ones(4))
    array([1, 1, 1, 1])
    >>> make_optional_arg_into_id_array(4, 0)
    array([0])
    >>> make_optional_arg_into_id_array(4, np.array([[1, 2], [3, 4]]))
    array([1, 2, 3, 4])
    """
    if len(args) == 0:
        ids = np.arange(number_of_elements, dtype=np.int)
    elif len(args) == 1:
        ids = as_id_array(np.asarray(args[0])).reshape((-1, ))
    else:
        raise ValueError('Number of arguments must be 0 or 1.')

    return ids


def get_functions_from_module(mod, pattern=None):
    """Get all the function in a module.

    Parameters
    ----------
    mod : module
        An instance of a module.
    pattern : str, optional
        Only get functions whose name match a regular expression.

    Returns
    -------
    dict
        Dictionary of functions contained in the module. Keys are the
        function names, values are the functions themselves.
    """
    import inspect
    import re

    funcs = {}
    for name, func in inspect.getmembers(mod, inspect.isroutine):
        if pattern is None or re.match(pattern, name):
            funcs[name] = func
    return funcs


def add_functions_to_class(cls, funcs):
    """Add functions as methods of a class.

    Parameters
    ----------
    cls : class
        A class.
    funcs : dict
        Dictionary of function names and instances.
    """
    for name, func in funcs.items():
        setattr(cls, name, func)


def add_module_functions_to_class(cls, module, pattern=None):
    """Add functions from a module to a class as methods.

    Parameters
    ----------
    cls : class
        A class.
    module : module
        An instance of a module.
    pattern : str, optional
        Only get functions whose name match a regular expression.
    """
    import inspect
    import imp
    import os

    caller = inspect.stack()[1]
    path = os.path.join(os.path.dirname(caller[1]), os.path.dirname(module))

    (module, _) = os.path.splitext(os.path.basename(module))

    mod = imp.load_module(module, *imp.find_module(module, [path]))

    funcs = get_functions_from_module(mod, pattern=pattern)
    add_functions_to_class(cls, funcs)
