.. :changelog:
 
Release History
----------------

0.12.6 (2017-06-07)
++++++++++++++++++++
- Eventlike objects are now usable as context managers like files
- 'pytest' now works corectly (with no args)
- Fixed up missing symbols in fanotify module
- reworked test suite to acomidate python2.7

0.12.5 (2017-04-07)
++++++++++++++++++++
- Removal of seccomp support
- Add FAN_MODIFY_DIR from latest linux release
- Add FAN_ALL_EVENTS

0.12.4 (2017-01-27)
++++++++++++++++++++
- Added environment variable to disable building of seccomp support
- Fixed up issue with imports on splice and timerfd
- Added memfd support
- Fix up tests
- Test suite now leaks less fd's
- Added CLONE_NEWCGROUP
- setns wrapper added (only low level stub was present)

0.12.3 (2017-01-27)
++++++++++++++++++++

- Added contributor file to keep a record of those who helped out
- fix up imports that where breaking on python3, preventing lib usage
- Document a 3rd party lib dependency that comes in handy

0.12.2 (2016-04-16)
++++++++++++++++++++

- Include missing build files

0.12.1 (2015-05-02)
++++++++++++++++++++

- Added stub for removed vmsplice() that raises NotImplemented
- Remove note about installing cffi first as it is no longer required since v0.12

0.12 (2015-04-02)
++++++++++++++++++

- Add support for new timer types including 'slack' timers and timers that can wake a system from suspend
- Hid the clone.C class as clone._C as it is not intended for general consumption
- Provided C implementation for pivot_root as it was not provided by glibc
- Migrated to cffi >= 1.0.0 to fix build bugs

**API Changes**

- Removed vmsplice() due to safety issues (does not copy bytes but maps live data, GC causes liveliness issues)

0.11.2 (2015-09-27)
++++++++++++++++++++

- Document cffi bootstrap issues in README

0.11.1 (2015-06-14)
++++++++++++++++++++

- Misc fixups to setup.py

**API Changes**

- Older Linux distros (debian < Jessie) to not provide libseccomp, disable this at setup.py time

**Bug Fixes**

- Older Linux distros do not provide setns via libc, a 'weak' dummy implementation is now provided to allow compliation to work

0.11 (2015-05-02)
++++++++++++++++++

- Make close on exec the default behavior for python 3 platforms
- Low level functions now accept a file-like or event-like object in addition to a fd
- New 'watch' function as a simple wrapper around inotify for ultra simple uses cases
- wait() on eventlike objects now accept a timeout value in seconds to specify the maximum ammount of
  time to wait for an event to occur

**API Changes**

- Argument order to fanotify_mark and high level API changed to have a more logical flow
- Timerfd code has been overhauled and is no longer compatible

**Bug Fixes**

- 'blocking' on Inotify objects was an internal flag and is now prefixed with '_' to denote its status
- Timerfd was created by default as CLOCK_MONOTONIC in contrast to other functions in butter
- Fixed bug that prevented compilation on 64bit machines with signalfd

0.10 (2015-03-20)
++++++++++++++++++

- errno to Exception mapping became a fixed part of the API (and unit tested)
- timerfd is now CLOCK_MONOTONIC by default
- Added Simpler TimerVal to replace Timerspec for timerfd
- Deprecated TimerStruct (will print a DeprecationWarning if such warnings have been turned on)
- OSError now returned instead of IOError. on python3 IOError = OSError so identical behavior will be observed
- Identical Error codes now return Identical Exceptions, except where there is a clear reason not o (eg InternalError)
- Errors due to incorrect arguments now all raise ValueError instead of ValueError or OSError

**Bug Fixes**

- C code now gets compiled at installation rather than first use
- Fixed up the name of an exception in error handling code leading to double exception
- pivot_root would return OSError rather than ValueError when incorect arguments were provided
- system.py was using its own definition of PermissionError, unify this with utils.py
- fanotify now raises PermissionError on EPERM instead of OSError (of which it is a subclass)

0.9.2 (2015-03-10)
+++++++++++++++++++

- Deprecating seccomp support in favour of official libseccomp python bindings

**Bug Fixes**

- Add __init__.py to asyncio dir so that async methods can be imported

0.9.1 (2015-01-05)
+++++++++++++++++++

**Bug Fixes**

- read_events was passing an undefined variable to actual implementations

0.9 (2014-05-24)
+++++++++++++++++

- Added eventfd support
- Added eventfd AsyncIO support
- Added timerfd support
- Added timerfd AsyncIO support
- Added Signalfd
- Added Signalfd AsyncIO support
- Added pthread_sigmask
- AsyncIO objects now have a close() method
- Converted all high level event objects to Eventlike objects
- Inotify events now have an is_dir_event property
- Added test suite

**Bug Fixes**

- Fixed issue with circular imports preventing python3.4 from working
- Fixed issue with python2.7 returning floats where python3 returned ints


0.8 (2014-05-17)
+++++++++++++++++

- Now works with python3.4 and higher
- 'from butter import \*' now imports the system module
- Added trove classification
- Added friendly properties to inotify event object
- Added friendly properties to fanotify event object
- FanotifyEvents now use less memory
- AsyncIO support for inotify on supported platforms
- AsyncIO support for fanotify on supported platforms

0.7 (2014-03-16)
+++++++++++++++++

- Added system.py module
- Added gethostname syscall
- Added sethostname syscall
- Added mount syscall
- Added umount syscall
- Added pivot_root syscall
- Added getpid syscall
- Added getppid syscall
- Documented all new syscalls

0.6 (2014-03-12)
+++++++++++++++++

- splice syscall documentation
- Added tee() syscall
- Added tee() example
- Added vmsplice() syscall
- Added vmsplice() example
- Updated setup.py to newer auto detecting version
- hide 'main' functions in splice module

0.5 (2014-03-11)
+++++++++++++++++

- Added splice() syscall

0.4 (2013-12-12)
+++++++++++++++++

- Refactor fanotify
- Refactor inotify
- Provide fanotify.str_to_events()
- Provide inotify.str_to_events()
- Add int to signal name mapping for inotify

0.3 (2013-11-20)
+++++++++++++++++

- Support for inotify
- Initial support for fanotify
- Initial support for seccomp
- Add function to peer inside kernel buffer and get amount of available bytes to read
  
**API Changes**

- removed unused old (non working) signalfd, eventfd, aio

0.2 (2013-11-20)
+++++++++++++++++

- Initial support for signalfd
- Initial support for eventfd
- Initial support for aio

