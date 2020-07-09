#!/usr/bin/env python
"""both _fanotify and fanotify module use these constants
so to avoid an import error lets place them in a separate 
module"""

from ._fanotify_c import lib as _lib
_l = locals()
for key in dir(_lib):
    if key.startswith('FAN_'):
        _l[key] = getattr(_lib, key)
del key, _lib, _l

