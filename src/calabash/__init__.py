from pipeline import source, sink
import common


def _get_tests():
    import doctest
    import inspect
    import sys
    import unittest

    def _from_module(module, object):
        """Backported fix for http://bugs.python.org/issue1108."""
        if module is None:
            return True
        elif inspect.getmodule(object) is not None:
            return module is inspect.getmodule(object)
        elif inspect.isfunction(object):
            return module.__dict__ is object.func_globals
        elif inspect.isclass(object):
            return module.__name__ == object.__module__
        elif hasattr(object, '__module__'):
            return module.__name__ == object.__module__
        elif isinstance(object, property):
            return True # [XX] no way not be sure.
        else:
            raise ValueError("object must be a class or function")
    finder = doctest.DocTestFinder()
    finder._from_module = _from_module

    suite = unittest.TestSuite()
    for name, module in sys.modules.iteritems():
        if name.startswith('calabash'):
            try:
                mod_suite = doctest.DocTestSuite(module, test_finder=finder)
            except ValueError:
                continue
            suite.addTests(mod_suite)
    return suite
