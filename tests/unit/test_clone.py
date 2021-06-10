#!/usr/bin/env python

from butter.clone import unshare, setns
import pytest

@pytest.mark.clone
def test_setns(mock):
    m = mock.patch('butter.clone._lib')
    m = mock.patch('butter.clone._lib.setns')
    m.return_value = 0
        
    setns(fd=5)
