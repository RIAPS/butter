#!/usr/bin/env python

import pytest
from butter._memfd import memfd_create, revoke, seal, flags, F_SEAL_WRITE
from butter.memfd import Memfd, MFD_ALLOW_SEALING
from butter.utils import PermissionError
import os

@pytest.fixture
def memfd():
    mem = Memfd(__name__, flags=MFD_ALLOW_SEALING)

    yield mem

    mem.close()

@pytest.fixture
def memfd_raw():
    fd = memfd_create(__name__,  flags=MFD_ALLOW_SEALING)
    
    yield fd

    os.close(fd)


@pytest.mark.memfd
def test_revoke(memfd_raw):
    revoke(memfd_raw, F_SEAL_WRITE)
    
@pytest.mark.memfd
def test_seal(memfd_raw):
    seal(memfd_raw)
    ## IOError being here is a compatibility hack for
    ## python2.7
    with pytest.raises((PermissionError, IOError)):
        revoke(memfd_raw, F_SEAL_WRITE)
        
@pytest.mark.memfd
def test_get_flags(memfd_raw):
    assert flags(memfd_raw) == 0
    revoke(memfd_raw, F_SEAL_WRITE)
    assert flags(memfd_raw) == F_SEAL_WRITE

@pytest.mark.memfd
def test_growable(memfd):
    assert memfd.growable
    memfd.growable = True # this should be a noop
    assert memfd.growable

    memfd.growable = False
    assert memfd.growable == False

@pytest.mark.memfd
def test_shrinkable(memfd):
    assert memfd.shrinkable
    memfd.shrinkable = True # this should be a noop
    assert memfd.shrinkable

    memfd.shrinkable = False
    assert memfd.shrinkable == False

@pytest.mark.memfd
def test_writable(memfd):
    assert memfd.writable
    memfd.writable = True # this should be a noop
    assert memfd.writable

    memfd.writable = False
    assert memfd.writable == False

@pytest.mark.memfd
def test_mmap(mocker, memfd):
    m = mocker.patch('butter.memfd.mmap')
    memfd.mmap(length=20)
    assert m.called
