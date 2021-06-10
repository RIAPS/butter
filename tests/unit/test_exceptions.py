#!/usr/bin/env python

from butter import eventfd, _eventfd
from butter import fanotify, _fanotify
from butter import inotify, _inotify
from butter import signalfd, _signalfd
from butter import _memfd
from butter.signalfd import SFD_CLOEXEC, SFD_NONBLOCK
from butter import timerfd, _timerfd
from butter._timerfd import TimerVal, CLOCK_REALTIME, CLOCK_MONOTONIC
from butter.utils import PermissionError, InternalError, UnknownError
from butter import clone
from butter import splice
from butter import system
from butter.system import Retry
from pytest import raises
from signal import SIGKILL
from os import devnull
import pytest
import errno

# monkey patch modeuls so we dont need to special case out code
splice.ffi = splice._ffi
system.ffi = system._ffi

@pytest.mark.parametrize('path,module,func,args,errno,exception', [
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.EINVAL, ValueError),
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.EMFILE, OSError),
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.ENFILE, OSError), # errno is diffrent to above
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.ENODEV, OSError),
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.ENOMEM, MemoryError),
 ('butter._eventfd.lib.eventfd', _eventfd, _eventfd.eventfd, (), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._fanotify.lib.fanotify_init', _fanotify, _fanotify.fanotify_init, (0,), errno.EINVAL, ValueError),
 ('butter._fanotify.lib.fanotify_init', _fanotify, _fanotify.fanotify_init, (0,), errno.EMFILE, OSError),
 ('butter._fanotify.lib.fanotify_init', _fanotify, _fanotify.fanotify_init, (0,), errno.ENOMEM, MemoryError),
 ('butter._fanotify.lib.fanotify_init', _fanotify, _fanotify.fanotify_init, (0,), errno.EPERM,  PermissionError),
 ('butter._fanotify.lib.fanotify_init', _fanotify, _fanotify.fanotify_init, (0,), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.EINVAL, ValueError),
 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.EBADF,  ValueError),
 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.ENOENT, ValueError),
 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.ENOMEM, MemoryError),
 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.ENOSPC, OSError),
 ('butter._fanotify.lib.fanotify_mark', _fanotify, _fanotify.fanotify_mark, (0, '/', 0, 0), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._inotify.lib.inotify_init1', _inotify, _inotify.inotify_init, (), errno.EINVAL, ValueError),
 ('butter._inotify.lib.inotify_init1', _inotify, _inotify.inotify_init, (), errno.EMFILE, OSError),
 ('butter._inotify.lib.inotify_init1', _inotify, _inotify.inotify_init, (), errno.ENFILE, OSError), # errno is diffrent to above
 ('butter._inotify.lib.inotify_init1', _inotify, _inotify.inotify_init, (), errno.ENOMEM, MemoryError),
 ('butter._inotify.lib.inotify_init1', _inotify, _inotify.inotify_init, (), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.EINVAL, ValueError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.EACCES, PermissionError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.EBADF, ValueError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.EFAULT, ValueError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.ENOENT, ValueError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.ENOSPC, OSError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.ENOMEM, MemoryError), 
 ('butter._inotify.lib.inotify_add_watch', _inotify, _inotify.inotify_add_watch, (0, '/', 0), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._inotify.lib.inotify_rm_watch', _inotify, _inotify.inotify_rm_watch, (0, 0), errno.EINVAL, ValueError),
 ('butter._inotify.lib.inotify_rm_watch', _inotify, _inotify.inotify_rm_watch, (0, 0), errno.EBADF, ValueError),
 ('butter._inotify.lib.inotify_rm_watch', _inotify, _inotify.inotify_rm_watch, (0, 0), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([], 0, 0xffff ^ (SFD_CLOEXEC|SFD_NONBLOCK)),  errno.EINVAL, ValueError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([], 0, SFD_CLOEXEC|SFD_NONBLOCK),  errno.EINVAL, ValueError), # FD is invalid (set flags just to ensure nothing blows up)
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.EBADF,  ValueError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.ENFILE, OSError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.EMFILE, OSError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.ENODEV, OSError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.ENOMEM, MemoryError),
 ('butter._signalfd.lib.signalfd', _signalfd, _signalfd.signalfd, ([],), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter._signalfd.lib.pthread_sigmask', _signalfd, _signalfd.pthread_sigmask, (0, SIGKILL), errno.EINVAL, ValueError),
 ('butter._signalfd.lib.pthread_sigmask', _signalfd, _signalfd.pthread_sigmask, (0, SIGKILL), errno.EFAULT, ValueError),
 ('butter._signalfd.lib.pthread_sigmask', _signalfd, _signalfd.pthread_sigmask, (0, SIGKILL), errno.EHOSTDOWN, UnknownError),

 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (0xffff ^ (CLOCK_REALTIME | CLOCK_MONOTONIC),), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (0xffff,), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (), errno.EMFILE, OSError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (), errno.ENFILE, OSError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (), errno.ENODEV, OSError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (), errno.ENOMEM, MemoryError),
 ('butter._timerfd.lib.timerfd_create', _timerfd, _timerfd.timerfd, (), errno.EHOSTDOWN, UnknownError),

 ('butter._timerfd.lib.timerfd_gettime', _timerfd, _timerfd.timerfd_gettime, (0,), errno.EBADF, ValueError),
 ('butter._timerfd.lib.timerfd_gettime', _timerfd, _timerfd.timerfd_gettime, (0,), errno.EFAULT, InternalError),
 ('butter._timerfd.lib.timerfd_gettime', _timerfd, _timerfd.timerfd_gettime, (0,), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_gettime', _timerfd, _timerfd.timerfd_gettime, (0,), errno.EHOSTDOWN, UnknownError),

 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal().repeats(seconds=999999999+1)), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal().repeats(nano_seconds=999999999+1)), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal().offset(seconds=999999999+1)), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal().offset(nano_seconds=999999999+1)), errno.EINVAL, ValueError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.EFAULT, InternalError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.EMFILE, OSError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.ENFILE, OSError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.ENODEV, OSError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.ENOMEM, MemoryError),
 ('butter._timerfd.lib.timerfd_settime', _timerfd, _timerfd.timerfd_settime, (0, TimerVal()), errno.EHOSTDOWN, UnknownError),

 ('butter.clone._lib.unshare', clone, clone.unshare, (0,), errno.EINVAL, ValueError),
 ('butter.clone._lib.unshare', clone, clone.unshare, (0,), errno.EPERM, PermissionError),
 ('butter.clone._lib.unshare', clone, clone.unshare, (0,), errno.EUSERS, PermissionError),
 ('butter.clone._lib.unshare', clone, clone.unshare, (0,), errno.ENOMEM, MemoryError),
 ('butter.clone._lib.unshare', clone, clone.unshare, (0,), errno.EHOSTDOWN, UnknownError),

 ('butter.clone._lib.setns', clone, clone.setns, (0,), errno.EBADF, ValueError),
 ('butter.clone._lib.setns', clone, clone.setns, (0,), errno.EINVAL, ValueError),
 ('butter.clone._lib.setns', clone, clone.setns, (0,), errno.EPERM, PermissionError),
 ('butter.clone._lib.setns', clone, clone.setns, (0,), errno.ENOMEM, MemoryError),
 ('butter.clone._lib.setns', clone, clone.setns, (0,), errno.EHOSTDOWN, UnknownError),

 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.EINVAL, ValueError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0, 20), errno.EINVAL, ValueError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.EBADF, ValueError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.EPIPE, ValueError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.ENOMEM, MemoryError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.EAGAIN, OSError),
 ('butter.splice._lib.splice', splice, splice.splice, (0, 0), errno.EHOSTDOWN, UnknownError),

 ('butter.splice._lib.tee', splice, splice.tee, (0, 0), errno.EINVAL, ValueError),
 ('butter.splice._lib.tee', splice, splice.tee, (0, 0), errno.ENOMEM, MemoryError),
 ('butter.splice._lib.tee', splice, splice.tee, (0, 0), errno.EHOSTDOWN, UnknownError),

 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.EINVAL, ValueError),
 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.EMFILE, OSError),
 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.ENFILE, OSError), # errno is diffrent to above
 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.ENODEV, OSError),
 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.ENOMEM, MemoryError),
 ('butter._memfd.lib.memfd_create', _memfd, _memfd.memfd_create, (), errno.EHOSTDOWN, UnknownError), # errno chosen as unused in our code

 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EACCES, PermissionError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EBUSY, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EFAULT, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EINVAL, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ELOOP, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EMFILE, OSError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENAMETOOLONG, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENODEV, OSError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENOENT, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENOMEM, MemoryError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENOTBLK, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENOTDIR, ValueError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.ENXIO, OSError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EPERM, PermissionError),
 ('butter.system._lib.mount', system, system.mount, ('/dev/null', '/', 'auto'), errno.EHOSTDOWN, UnknownError),

 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EAGAIN, Retry),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EBUSY, ValueError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EFAULT, ValueError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EINVAL, ValueError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.ENAMETOOLONG, ValueError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.ENOENT, ValueError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.ENOMEM, MemoryError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EPERM, PermissionError),
 ('butter.system._lib.umount2', system, system.umount, ('/'), errno.EHOSTDOWN, UnknownError),

 ('butter.system._lib.pivot_root', system, system.pivot_root, ('/', '/'), errno.EINVAL, ValueError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, (devnull, '/'), errno.ENOTDIR, ValueError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, ('/', devnull), errno.ENOTDIR, ValueError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, (devnull, devnull), errno.ENOTDIR, ValueError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, ('/', '/'), errno.EBUSY, ValueError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, ('/', '/'), errno.EPERM, PermissionError),
 ('butter.system._lib.pivot_root', system, system.pivot_root, ('/', '/'), errno.EHOSTDOWN, UnknownError),

 ('butter.system._lib.sethostname', system, system.sethostname, ('foobar',), errno.EFAULT, ValueError),
 ('butter.system._lib.sethostname', system, system.sethostname, ('foobar',), errno.EINVAL, ValueError),
 ('butter.system._lib.sethostname', system, system.sethostname, ('foobar',), errno.EPERM, PermissionError),
 ('butter.system._lib.sethostname', system, system.sethostname, ('foobar',), errno.EHOSTDOWN, UnknownError),

 ('butter.system._lib.gethostname', system, system.gethostname, (), errno.EFAULT, ValueError),
 ('butter.system._lib.gethostname', system, system.gethostname, (), errno.EINVAL, ValueError),
 ('butter.system._lib.gethostname', system, system.gethostname, (), errno.ENAMETOOLONG, InternalError),
 ('butter.system._lib.gethostname', system, system.gethostname, (), errno.EPERM, PermissionError),
 ('butter.system._lib.gethostname', system, system.gethostname, (), errno.EHOSTDOWN, UnknownError),
 ])
@pytest.mark.unit
def test_exception(mocker, path, module, func, args, errno, exception):
    """Test the mapping of kernel returned error codes to python Exceptions"""
    # patch the _lib object as we cant patch c objects
    m = mocker.patch(".".join(path.split('.')[:-1]))
    # patch the underlying function as exposed by cffi
    m = mocker.patch(path)
    # -1 forces most of our code to check ffi.errno
    m.return_value = -1
    
    # Make the C level errno the val we want
    module.ffi.errno = errno
    
    # Call the same function as the user and wait for it to blow up
    with raises(exception):
        func(*args)
