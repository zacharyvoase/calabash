# -*- coding: utf-8 -*-

import re

from calabash.pipeline import pipe


@pipe
def echo(item):
    """
    Yield a single item. Equivalent to ``iter([item])``, but nicer-looking.

        >>> list(echo(1))
        [1]
        >>> list(echo('hello'))
        ['hello']
    """
    yield item

@pipe
def cat(*args, **kwargs):
    r"""
    Read a file. Passes directly through to a call to `open()`.

        >>> src_file = __file__.replace('.pyc', '.py')
        >>> for line in cat(src_file):
        ...     if line.startswith('def cat'):
        ...          print repr(line)
        'def cat(*args, **kwargs):\n'
    """
    return iter(open(*args, **kwargs))


@pipe
def curl(url):
    """
    Fetch a URL, yielding output line-by-line.

        >>> UNLICENSE = 'http://unlicense.org/UNLICENSE'
        >>> for line in curl(UNLICENSE): # doctest: +SKIP
        ...     print line,
        This is free and unencumbered software released into the public domain.
        ...
    """
    import urllib2
    conn = urllib2.urlopen(url)
    try:
        line = conn.readline()
        while line:
            yield line
            line = conn.readline()
    finally:
        conn.close()


@pipe
def grep(stdin, pattern_src):
    """
    Filter strings on stdin for the given regex (uses :func:`re.search`).

        >>> list(iter(['cat', 'cabbage', 'conundrum', 'cathedral']) | grep(r'^ca'))
        ['cat', 'cabbage', 'cathedral']
    """
    pattern = re.compile(pattern_src)
    for line in stdin:
        if pattern.search(line):
            yield line


@pipe
def sed(stdin, pattern_src, replacement, exclusive=False):
    """
    Apply :func:`re.sub` to each line on stdin with the given pattern/repl.

        >>> list(iter(['cat', 'cabbage']) | sed(r'^ca', 'fu'))
        ['fut', 'fubbage']

    Upon encountering a non-matching line of input, :func:`sed` will pass it
    through as-is. If you want to change this behaviour to only yield lines
    which match the given pattern, pass `exclusive=True`::

        >>> list(iter(['cat', 'nomatch']) | sed(r'^ca', 'fu'))
        ['fut', 'nomatch']
        >>> list(iter(['cat', 'nomatch']) | sed(r'^ca', 'fu', exclusive=True))
        ['fut']
    """
    pattern = re.compile(pattern_src)
    for line in stdin:
        match = pattern.search(line)
        if match:
            yield (line[:match.start()] +
                   match.expand(replacement) +
                   line[match.end():])
        elif not exclusive:
            yield line


@pipe
def pretty_printer(stdin, **kwargs):
    """
    Pretty print each item on stdin and pass it straight through.

        >>> for item in iter([{'a': 1}, ['b', 'c', 3]]) | pretty_printer():
        ...     pass
        {'a': 1}
        ['b', 'c', 3]
    """
    import pprint
    for item in stdin:
        pprint.pprint(item, **kwargs)
        yield item


@pipe
def map(stdin, func):
    """
    Map each item on stdin through the given function.

        >>> list(xrange(5) | map(lambda x: x + 2))
        [2, 3, 4, 5, 6]
    """
    for item in stdin:
        yield func(item)


@pipe
def filter(stdin, predicate):
    """
    Only pass through items for which `predicate(item)` is truthy.

        >>> list(xrange(5) | filter(lambda x: x % 2 == 0))
        [0, 2, 4]
    """
    for item in stdin:
        if predicate(item):
            yield item


@pipe
def sh(stdin, command=None, check_success=False):
    r"""
    Run a shell command, send it input, and produce its output.

        >>> print ''.join(echo("h\ne\nl\nl\no") | sh('sort -u'))
        e
        h
        l
        o
        <BLANKLINE>
        >>> for line in sh('echo Hello World'):
        ...     print line,
        Hello World
        >>> for line in sh('false', check_success=True):
        ...     print line, # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        CalledProcessError: Command '['false']' returned non-zero exit status 1
    """
    import subprocess
    import shlex

    if command is None:
        stdin, command = (), stdin

    if isinstance(command, basestring):
        command = shlex.split(command)

    pipe = subprocess.Popen(command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

    try:
        for line in stdin:
            pipe.stdin.write(line)
        pipe.stdin.close()
        for line in pipe.stdout:
            yield line
    finally:
        result = pipe.wait()
        if check_success and result != 0:
            raise subprocess.CalledProcessError(result, command)
