import io

from ._msgpack import pack_stream, unpack_stream


def pack(obj):
    """Pack object into data."""
    with io.BytesIO() as stream:
        pack_stream(stream, obj)
        data = stream.getvalue()
    return data


def unpack(data):
    """Unpack data into object."""
    with io.BytesIO(data) as stream:
        obj = unpack_stream(stream)
        excess_data = stream.read()
    return obj, excess_data
