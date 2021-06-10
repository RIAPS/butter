#!/usr/bin/env python

import pytest

from butter.build import clone, eventfd, fanotify, inotify
from butter.build import memfd, signalfd, splice
from butter.build import system, timerfd, utils

from utils import TemporaryDirectory


@pytest.mark.build
@pytest.mark.parametrize('module', [clone, 
                                    eventfd,
                                    fanotify,
                                    inotify,
                                    memfd,
                                    signalfd,
                                    splice,
                                    system,
                                    timerfd,
                                    utils])
def test_build(module):
    with TemporaryDirectory() as tmpdir:
        module.ffi.compile(tmpdir=tmpdir)

