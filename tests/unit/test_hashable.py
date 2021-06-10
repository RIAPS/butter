from butter.eventfd import Eventfd
from butter.fanotify import Fanotify
from butter.inotify import Inotify
from butter.signalfd import Signalfd
from butter.timerfd import Timer
from butter.memfd import Memfd
import pytest


@pytest.fixture(params=[Eventfd, Fanotify, Inotify, Signalfd, Timer, Memfd])
def obj(request):
    Obj = request.param
    o1 = Obj.__new__(Obj)
    o2 = Obj.__new__(Obj)
    
    yield (o1, o2)
    
    try: o1.close()
    except ValueError: pass
    
    try: o2.close()
    except ValueError: pass

@pytest.mark.unit
def test_equals_same(obj):
    obj1, obj2 = obj
    fd_backup = (obj1._fd, obj2._fd)
    obj1._fd = 1
    obj2._fd = 1

    assert obj1 == obj2, '2 Identical objects are comparing as diffrent'

    obj1._fd, obj2._fd = fd_backup

def test_equals_diffrent(obj):
    obj1, obj2 = obj
    fd_backup = (obj1._fd, obj2._fd)
    obj1._fd = 1
    obj2._fd = 2

    assert obj1 != obj2, '2 Diffrent objects are comparing as equivlent'

    obj1._fd, obj2._fd = fd_backup

def test_hashable(obj):
    obj1, obj2 = obj
    fd_backup = (obj1._fd, obj2._fd)

    obj1._fd = 1
    assert isinstance(hash(obj), int), 'hash of object is not an int'
    assert {obj1: None}, 'Object cant be used as a key in a dict (not hashable)'

    obj1._fd, obj2._fd = fd_backup
