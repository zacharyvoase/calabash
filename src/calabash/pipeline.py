# -*- coding: utf-8 -*-

from functools import wraps


class PipeLine(object):

    """
    A coroutine wrapper which enables pipelining syntax.

    :class:`PipeLine` allows you to flatten once-nested code just by wrapping
    your generators. The class provides combinators in the form of operators,
    allowing you to plug two generators together without having to nest lots of
    function calls. For example::

        >>> def summer(stdin):
        ...     sum = 0
        ...     for item in stdin:
        ...         sum += item
        ...         yield sum
        >>> pipeline = PipeLine(lambda: iter([1, 2, 3, 4])) | PipeLine(summer)
        >>> pipeline
        <PipeLine: <lambda> | summer>
        >>> for item in pipeline:
        ...     print item
        1
        3
        6
        10

    The yielded output of each generator in the chain becomes the input for the
    next. The rules for writing a pipeline function are simple:
    :class:`PipeLine` requires a callable which accepts a single argument (the
    input), and returns an iterator. The only exception is the first part of
    the pipeline, which should accept no arguments (as there will be no input).

    For convenience, two decorators have been provided in this module:
    :func:`source` and :func:`sink`. :func:`source` is for writing functions
    which only produce output, but take no input::

        >>> @source
        ... def my_generator():
        ...     yield 1
        ...     yield 2
        ...     yield 3
        >>> pl = my_generator()
        >>> pl
        <PipeLine: my_generator>
        >>> for item in pl:
        ...     print item
        1
        2
        3

    :func:`sink` is for writing functions which do accept input::

        >>> @sink
        ... def add_one(input):
        ...     for item in input:
        ...         yield item + 1
        >>> pl = my_generator() | add_one()
        >>> pl
        <PipeLine: my_generator | add_one>
        >>> for item in pl:
        ...     print item
        2
        3
        4

    With :func:`source` and :func:`sink`, your functions can also accept other
    parameters::

        >>> @sink
        ... def adder(input, amount):
        ...     for item in input:
        ...         yield item + amount
        >>> pl = my_generator() | adder(3)
        >>> pl
        <PipeLine: my_generator | adder>
        >>> for item in pl:
        ...     print item
        4
        5
        6
    """

    __slots__ = ('coro_func',)

    def __init__(self, coro_func):
        self.coro_func = coro_func

    @property
    def __name__(self):
        return self.coro_func.__name__

    def __repr__(self):
        return '<PipeLine: %s>' % getattr(self.coro_func, '__name__', repr(self.coro_func))

    def __or__(self, target):
        return target.__ror__(self)

    def __ror__(self, source):
        def pipe():
            return self.coro_func(iter(source))
        pipe.__name__ = '%s | %s' % (
                getattr(source, '__name__', repr(source)),
                getattr(self.coro_func, '__name__', repr(self.coro_func)))
        return PipeLine(pipe)

    def __iter__(self):
        return self.coro_func()


def source(func):
    """
    Wrap a function as a pipeline source (i.e. one that does not accept stdin).

        >>> @source
        ... def echoer(items):
        ...     for item in items:
        ...         yield item
        >>> e = echoer([1, 2, 3])
        >>> e
        <PipeLine: echoer>
        >>> for item in e:
        ...     print item
        1
        2
        3
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        coro_func = wraps(func)(lambda: func(*args, **kwargs))
        return PipeLine(coro_func)
    return wrapper


def sink(func):
    """
    Wrap a function as a pipeline sink (i.e. one that accepts stdin).

        >>> @sink
        ... def printer(stdin, outfile=None):
        ...     for item in stdin:
        ...         print >>outfile, item
        ...         yield item
        >>> p = printer()
        >>> p
        <PipeLine: printer>
        >>> output = list(iter([1, 2, 3, 4, 5]) | p)
        1
        2
        3
        4
        5
        >>> output
        [1, 2, 3, 4, 5]
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        @wraps(func)
        def coro_func(stdin=()):
            return func(stdin, *args, **kwargs)
        return PipeLine(coro_func)
    return wrapper
