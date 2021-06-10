#!/usr/bin/env python

import pytest
from butter.splice import vmsplice

@pytest.mark.vmsplice
def test_vmsplice():
    with pytest.raises(NotImplementedError):
        vmsplice(None, None)
