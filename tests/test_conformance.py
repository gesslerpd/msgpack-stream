from msgpack import packb, unpackb
from msgpack_stream import pack, unpack

import copy


obj = {
    b"bytearray": b"\x00\x01\x02\x03\x04",
    "string": "🐍",
    "list": [0, 1.0, None, "", b"", True, {}],
    "int": -1,
    "uint": 1,
    "float": 3.1416,
    "none": None,
    "boolean": True,
    "test": [],
}

obj["object"] = copy.deepcopy(obj)


obj_extra = {None: None, 3: 3, -1: -1, True: True, False: "hey", 1.1: 1.1}

for i in range(64):
    li = obj["test"]
    pow2 = 2**i
    pow21 = pow2 - 1
    pow211 = pow2 + 1
    li.extend(
        [
            pow2,
            pow21,
            pow211,
            -pow2,
            -pow21,
        ]
    )
    li.append(2**64 - 1)
    li.append(-(2**63))

for i in range(2**18):
    obj[f"test{i}"] = i


def test_conformance():
    data = packb(obj)
    assert pack(obj) == data
    assert unpackb(data) == obj
    unpacked_obj, _ = unpack(data)
    assert unpacked_obj == obj


def test_extra():
    data = pack(obj_extra)
    unpacked_obj, _ = unpack(data)
    assert unpacked_obj == obj_extra
