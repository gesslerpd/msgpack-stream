from msgpack_stream import msgpack_t

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
    msgpack_t.pack(stream, obj)
    msgpack_t.pack(stream, obj)
    stream.seek(0)
    assert msgpack_t.unpack(stream) == obj
    assert msgpack_t.unpack(stream) == obj
    stream.close()
