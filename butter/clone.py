#!/usr/bin/env python

from .utils import PermissionError, UnknownError
import errno

from ._clone import ffi
from ._clone import lib as _lib

CLONE_NEWNS = _lib.CLONE_NEWNS
CLONE_NEWUTS = _lib.CLONE_NEWUTS
CLONE_NEWIPC = _lib.CLONE_NEWIPC
CLONE_NEWUSER = _lib.CLONE_NEWUSER
CLONE_NEWPID = _lib.CLONE_NEWPID
CLONE_NEWNET = _lib.CLONE_NEWNET

try:
    CLONE_NEWCGROUP = _lib.CLONE_NEWCGROUP
except AttributeError:
    pass

SETNS_ANY = 0

def unshare(flags):
    """Unshare the current namespace and create a new one

    Arguments
    ----------
    :param int flags: The flags controlling which namespaces to unshare

    Flags
    ------
    CLONE_NEWNS: Unshare the mount namespace causing mounts in this namespace
                 to not be visible to the parent namespace
    CLONE_NEWCGROUP: Hide existing cgroups and make the process see its resident cgroup
                     as the top of the tree in the cgroup filesystem
    CLONE_NEWUTS: Unshare the system hostname allowing it to be changed independently
                  to the rest of the system
    CLONE_NEWIPC: Unshare the IPC namespace 
    CLONE_NEWUSER: Unshare the UID space allowing UIDs to be remapped to the parent
    CLONE_NEWPID: Unshare the PID space allowing remapping of PIDs relative to the parent
    CLONE_NEWNET: Unshare the network namespace, creating a separate set of network
                  interfaces/firewall rules

    Exceptions
    -----------
    :raises ValueError: Invalid value in flags
    """
    fd = _lib.unshare(flags)

    if fd < 0:
        err = ffi.errno
        if err == errno.EINVAL:
            raise ValueError("Invalid value in flags")
        elif err == errno.EPERM:
            raise PermissionError("Process in chroot or has incorrect permissions")
        elif err == errno.EUSERS:
            raise PermissionError("CLONE_NEWUSER specified but max user namespace nesting has been reached")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return fd

def setns(fd, nstype=SETNS_ANY):
    """Join an existing namespace

    Arguments
    ----------
    :param int nstype: Restrict the type of namespace the process will join

    Flags
    ------
    SETNS_ANY: Allows any namespace to be joined (Default)
    CLONE_NEWNS: Unshare the mount namespace causing mounts in this namespace
                 to not be visible to the parent namespace
    CLONE_NEWCGROUP: Hide existing cgroups and make the process see its resident cgroup
                     as the top of the tree in the cgroup filesystem
    CLONE_NEWUTS: Unshare the system hostname allowing it to be changed independently
                  to the rest of the system
    CLONE_NEWIPC: Unshare the IPC namespace 
    CLONE_NEWUSER: Unshare the UID space allowing UIDs to be remapped to the parent
    CLONE_NEWPID: Unshare the PID space allowing remapping of PIDs relative to the parent
    CLONE_NEWNET: Unshare the network namespace, creating a separate set of network
                  interfaces/firewall rules

    Exceptions
    -----------
    :raises ValueError: The file descriptor is invalid
    :raises ValueError: The file descriptor does not match nstype
    :raises ValueError: The process is multithreadded and attempted to join a user namespace
    :raises ValueError: The process is multithreadded and an error occured
    :raises ValueError: The process shares filesystem state (CLONE_FS) and attemtped to join a user namespace
    :raises ValueError: The process attempted to join a namespace it was already part of
    :raises PermissionError: Process does not have the required capabilities (CAP_SYS_ADMIN)
    :raises MemoryError: Insufficent kernel memory avalible
    """
    ret = _lib.setns(fd, nstype)

    if ret < 0:
        err = ffi.errno
        if err == errno.EBADF:
            raise ValueError("File descriptor is not valid")
        if err == errno.EINVAL:
            raise ValueError("File descriptor does not match nstype or process attempted to join namespace it was already part of")
        elif err == errno.EPERM:
            raise PermissionError("Process does not have the required capabilities (CAP_SYS_ADMIN)")
        elif err == errno.ENOMEM:
            raise MemoryError("Insufficent kernel memory available")
        else:
            # If you are here, its a bug. send us the traceback
            raise UnknownError(err)

    return fd
    
 

def main():
    import os, errno, sys
    
#    ret = _lib.__clone(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS, ffi.NULL)
#    ret = _lib.__clone(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL)

    ret = _lib.unshare(CLONE_NEWNET|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWNS)
#    ret = _lib.unshare(CLONE_ALL)
    if ret >= 0:
#        with open("/proc/self/uid_map", "w") as f:
#            f.write("0 0 1\n")
        os.execl('/bin/bash', 'bash')
    else:
        print(ret, ffi.errno, errno.errorcode[ffi.errno])
        print("failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
