from msgpack_stream import pack_stream, unpack_stream

import io


obj = {
    b"bytearray": b"\x00\x01\x02\x03\x04",
    "string": "🐍",
    "list": [0, 1.0, None, "", b"", True, {}],
    "int": -1,
    "uint": 1,
    "float": 3.1416,
    "none": None,
    "boolean": True,
    "object": {
        None: None,
        3: 3,
        -1: -1,
        True: True,
        False: "hey",
    },
}


def test_stream():
    stream = io.BytesIO()
    pack_stream(stream, obj)
    pack_stream(stream, obj)
    stream.seek(0)
    assert unpack_stream(stream) == obj
    assert unpack_stream(stream) == obj
    stream.close()
