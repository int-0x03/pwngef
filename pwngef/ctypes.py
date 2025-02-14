"""On-the-fly endianness switching for ctypes structures.

We cannot make use of ctypes.LittleEndianStructure and ctypes.BigEndianStructure,
since these use metaclass hooks to catch _fields_ being **set** when the class
is declared.

We need to catch on the fly.  We do this by swapping out the base classes of the
Structure type, and incurring a performance penalty for foreign-endianness targets.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ctypes
import sys

import pwngef.arch
import pwngef.events

module = sys.modules[__name__]


@pwngef.events.new_objfile
def update():
    global module

    if pwngef.arch.endian == 'little':
        Structure = ctypes.LittleEndianStructure
    else:
        Structure = ctypes.BigEndianStructure

    module.__dict__.update(locals())


update()
