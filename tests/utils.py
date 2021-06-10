#!/usr/bin/env python
from tempfile import mkdtemp
import weakref as _weakref
from shutil import rmtree as _rmtree
from contextlib import contextmanager

import platform

if platform.python_version_tuple() < ('3', '0', '0'):
    @contextmanager
    def TemporaryDirectory(suffix="", prefix='tmp', dir=None):
        try:
            name = mkdtemp(suffix, prefix, dir)
            yield name
        finally:
            _rmtree(name)
else:
    from tempfile import TemporaryDirectory
