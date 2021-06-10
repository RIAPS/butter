from butter.eventfd import Eventfd
from butter.fanotify import Fanotify
from butter.inotify import Inotify
from butter.signalfd import Signalfd
from butter.timerfd import Timer
from butter.memfd import Memfd

from butter import utils
from mock import patch

import pytest
import os

@pytest.fixture(params=[Eventfd, Fanotify, Inotify, Signalfd, Timer, Memfd])
def obj(request):
    Obj = request.param
    o = Obj.__new__(Obj)
    
    return o

@pytest.mark.eventlike
@pytest.mark.unit
def test_fd_closed(mocker, obj):
    """Ensure you cant close the same fd twice (as it may be reused)"""
    obj._fd = -1 # invalid but unlikley to cause issues
                 # if real close is called

    f = mocker.patch('butter.utils._close')
    f.side_effect = ValueError()
    with pytest.raises(ValueError):
        obj.close()

    f.assert_called()

@pytest.mark.eventlike
@pytest.mark.unit
def test_fd_contextmanager(mocker, obj):
    """Ensure close() is called when used as a context manager"""
    obj._fd = -1 # invalid but unlikley to cause issues
                 # if real close is called

    f = mocker.patch('butter.utils._close')
    with obj:
        pass

    f.assert_called()
