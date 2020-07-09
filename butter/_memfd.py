#!/usr/bin/env python
"""eventfd: maintain an atomic counter inside a file descriptor"""
from .utils import UnknownError, CLOEXEC_DEFAULT
from cffi import FFI
import errno

from ._memfd_c import ffi
from ._memfd_c import lib

from fcntl import fcntl

MFD_CLOEXEC = lib.MFD_CLOEXEC
MFD_ALLOW_SEALING = lib.MFD_ALLOW_SEALING

F_ADD_SEALS = lib.F_ADD_SEALS
F_GET_SEALS = lib.F_GET_SEALS
F_SEAL_SEAL = lib.F_SEAL_SEAL
F_SEAL_SHRINK = lib.F_SEAL_SHRINK
F_SEAL_GROW = lib.F_SEAL_GROW
F_SEAL_WRITE = lib.F_SEAL_WRITE

import platform
if platform.python_version_tuple() < ('3', '0', '0'):
    def bytes(s, encoding):
        if isinstance(s, str):
            return s.encode(encoding)
        return s
        
def memfd_create(name='', flags=0, closefd=CLOEXEC_DEFAULT):
    """Create a new memory backed file descriptor, this can be mmap'd
    into a processes address space or the fd passed to another program
    to allow for shared memory without a filename
    
    Arguments
    ----------
    :param int flags: Flags to specify extra options
    :param bool closefd: Close the fd when a new process is exec'd
        
    Flags
    ------
    MFD_CLOEXEC: Close the eventfd when executing a new program
    MFD_ALLOW_SEALING: Allow sealing of this file, preventing operations 
        such as resize or writing
    
    Returns
    --------
    :return: The file descriptor representing the eventfd
    :rtype: int
    
    Exceptions
    -----------
    :raises ValueError: Invalid value in flags or name too long
    :raises OSError: Max per process FD limit reached
    :raises OSError: Max system FD limit reached
    :raises OSError: Could not mount (internal) anonymous inode device
    :raises MemoryError: Insufficient kernel memory
    """
    assert isinstance(flags, int), "Flags must be an integer"
    
    if closefd:
        flags |= MFD_CLOEXEC

    name = bytes(name, 'UTF-8')        
    fd = lib.memfd_create(name, flags)
    
    if fd < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid value in flags or name too long")
        elif err == errno.EMFILE:
            raise OSError("Max per process FD limit reached")
        elif err == errno.ENFILE:
            raise OSError("Max system FD limit reached")
        elif err == errno.ENODEV:
            raise OSError("Could not mount (internal) anonymous inode device")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return fd


def seal(fd):
    """Prevent a file descriptor from ahving futher permissions removed"""
    error = fcntl(fd, F_ADD_SEALS, F_SEAL_SEAL)
    if error < 0:
        if ffi.errno == errno.EPERM:
            raise ValueError("This file has already been sealed")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

def revoke(fd, flags):
    """Revoke privileges on a file descriptor"""
    error = fcntl(fd, F_ADD_SEALS, flags)
    if error < 0:
        if ffi.errno == errno.EPERM:
            raise ValueError("This file has already been sealed")
        elif ffi.errno == errno.EBUSY:
            raise ValueError("Writable mappings exist for this file")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

def flags(fd):
    """Obtain the sealining flags for a given file descriptor"""
    error = fcntl(fd, F_GET_SEALS)
    if error < 0:
        if ffi.errno == errno.EINVAL:
            raise ValueError("File does not support sealing")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)
    flags = error # this is a noop for readibility

    return flags
