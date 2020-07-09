#!/usr/bin/env python

from cffi import FFI

ffi = FFI()

ffi.cdef("""
#define MFD_CLOEXEC ...
#define MFD_ALLOW_SEALING ...
                           
#define F_ADD_SEALS ...
#define F_GET_SEALS ...
#define F_SEAL_SEAL ...
#define F_SEAL_SHRINK ...
#define F_SEAL_GROW ...
#define F_SEAL_WRITE ...

int memfd_create(const char *name, unsigned int flags);
""")

ffi.set_source("_memfd_c", """
#include <linux/memfd.h>
#include <linux/fcntl.h>
#include <sys/syscall.h>

int memfd_create(const char *name, unsigned int flags){;
    return syscall(SYS_memfd_create, name, flags);
};
""", libraries=[])

if __name__ == "__main__":
    ffi.compile()
