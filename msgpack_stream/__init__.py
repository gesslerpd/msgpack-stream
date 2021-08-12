"""Pure Python stream based implementation of msgpack"""

from ._io import pack as packb, unpack as unpackb
from ._msgpack import msgpack_t


def pack(obj):
    """Pack object into data."""
    return packb(msgpack_t, obj)


def unpack(data):
    """Unpack data into object."""
    return unpackb(msgpack_t, data)
