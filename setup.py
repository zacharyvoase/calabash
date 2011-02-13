#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path as p

from distribute_setup import use_setuptools; use_setuptools()
from setuptools import setup, find_packages

VERSION = open(p.join(p.dirname(p.abspath(__file__)), 'VERSION')).read().strip()

setup(
    name             = 'calabash',
    version          = VERSION,
    author           = "Zachary Voase",
    author_email     = "z@zacharyvoase.com",
    url              = 'http://github.com/zacharyvoase/calabash',
    description      = "Bash-style pipelining syntax for Python generators.",
    packages         = find_packages(where='src'),
    package_dir      = {'': 'src'},
    test_suite       = 'calabash._get_tests',
)
