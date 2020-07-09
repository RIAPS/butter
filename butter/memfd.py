#!/usr/bin/env python
"""memfd: Create a memory backed non-persistent file that has no name on the filesystem

Memfd files are useful as temporary files or as buffers in IPC situations such as
window managers or any case where an area of memory needs to be shared between programs.

Memfd objects have the concept of 'sealing' which revokes certain actions from affecting
the area of memory, this includes the ability to revoke writability, the ability to 
shrink and grow the memory area. These are applied instantaneously (not on open() as
normal unix permissions are) and apply to all processes with that memory region open
ie the permissions are not 'per fd' as is normally the case.

Regions can also be sealed, preventing further modification of memory region rights. 
"""

from .utils import Eventlike as _Eventlike

from ._memfd import MFD_CLOEXEC, MFD_ALLOW_SEALING
from ._memfd import F_SEAL_SHRINK, F_SEAL_GROW, F_SEAL_WRITE
from ._memfd import memfd_create
from ._memfd import revoke, seal, flags
from .utils import CLOEXEC_DEFAULT as _CLOEXEC_DEFAULT

from mmap import mmap
from mmap import ACCESS_COPY, ACCESS_READ, ACCESS_WRITE
from mmap import PROT_READ, PROT_WRITE, PROT_EXEC
from mmap import MAP_ANON, MAP_ANONYMOUS, MAP_DENYWRITE, MAP_EXECUTABLE, MAP_PRIVATE, MAP_SHARED

class Memfd(_Eventlike):
    def __init__(self, name='', inital_value=0, flags=0, closefd=_CLOEXEC_DEFAULT):
        """Create a new Memfd object

        Arguments
        ----------
        :param int name: Name to identify the memfd region (not required)
        :param int flags: Flags to specify extra options
        
        Flags
        ------
        MFD_CLOEXEC: Close the eventfd when executing a new program
        MFD_ALLOW_SEALING: Allow sealing of the memfd region (writing/shrinking/growing support)
        """
        super(self.__class__, self).__init__()
        self._fd = memfd_create(name, flags, closefd=closefd)
        self._name = name
        
    @property
    def shrinkable(self):
        """Indicates if this memfd region can be shrunk or truncated via ftruncate()"""
        return False if self.flags & F_SEAL_SHRINK else True
    
    @shrinkable.setter
    def shrinkable(self, shrinkable):
        if not shrinkable:
            self.revoke(F_SEAL_SHRINK)
    
    @property
    def growable(self):
        """Indicates if this memfd region can be extended or 'grown' via ftruncate()"""
        return False if self.flags & F_SEAL_GROW else True

    @growable.setter
    def growable(self, growable):
        if not growable:
            self.revoke(F_SEAL_GROW)
        
    @property
    def writable(self):
        """Indicates if this memfd region is writable"""
        # Inverted logic, flags indicate ability is 'sealed'
        # while user cares about permission they have via verb
        return False if self.flags & F_SEAL_WRITE else True
        
    @writable.setter
    def writable(self, writable):
        if not writable:
            self.revoke(F_SEAL_WRITE)

    def revoke(self, flags):
        """Revoke multiple permissions in one go as opposed to using the shrinkable, growable, writable accessors
        
        This is mainly used to avoid calling fcntl multiple times.

        Arguments
        ----------
        :param int flags: Flags to specify extra options

        Flags
        ------
        F_SEAL_WRITE: Seal the ability to 'write' to the fd, preventing modification
        F_SEAL_SHRINK: Seal the ability to shrink the file via ftruncate() 
        F_SEAL_GROW: Seal the ability to expand or grow the file via ftruncate() or writes
        
        Note: Changes to permissions take affect immediately and apply to the file represented
        by the fd and not the fd itself. You will be unable to have 2 fd's point to the same
        memfd region with different seal permissions.
        """
        revoke(self._fd, flags)

    def seal(self):
        """Seal the file (not the file descriptor but all refrences to the file)
        preventing futher modification of permissions
        """
        seal(self._fd)

    @property
    def flags(self):
        """Get a copy of the current sealining flags of the memfd"""
        return flags(self._fd)

    def mmap(self,
             length,
             flags=0,
             prot=PROT_READ|PROT_WRITE|PROT_EXEC,
             access=ACCESS_COPY|ACCESS_READ|ACCESS_WRITE,
             offset=0):
        """mmap the memfd area
        
        accepts the same arguments as mmap.mmap() with the execption that fd is set
        to the fd of the memfd this method is bound to.
        """
        return mmap(self._fd, length, flags, prot, access, offset)


    def __repr__(self):
        fd = "closed" if self.closed() else self.fileno()
        return "<{} fd={} name='{}'>".format(self.__class__.__name__, fd, self._name)

