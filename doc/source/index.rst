Calabash Documentation
======================

Calabash aims to bring bash-style pipelining to Python generators.

A short example::

    >>> from calabash.common import grep
    >>> pl = iter(['python', 'ruby', 'jython']) | grep(r'yt')
    >>> pl
    <PipeLine: iter | grep>
    >>> for item in pl:
    ...     print item
    python
    jython

To see some examples of simple but useful pipeline components, check out the
:mod:`calabash.common` module. To get started writing your own, read the
:class:`~calabash.pipeline` documentation.

Installation
------------

You can get the module from PyPI::

    pip install calabash


Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

    pipeline
    common
