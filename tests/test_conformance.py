from msgpack import packb, unpackb
from msgpack_stream import pack, unpack

import copy


obj = {
    b"bytearray": b"\x00\x01\x02\x03\x04",
    "string": "🐍",
    "list": [0, 1.0, None, "", b"", True, {}, {f"{i}": i for i in range(0x10000)}],
    "int": -1,
    "uint": 1,
    "float": 3.1416,
    "none": None,
    "boolean": True,
    "test": [
        [
            power_of_2,
            power_of_2 - 1,
            power_of_2 + 1,
            -power_of_2,
            -(power_of_2 - 1),
        ]
        for i in range(64)
        if (power_of_2 := 2**i)
    ],
}

obj["object"] = copy.deepcopy(obj)


obj["list_b1"] = [1] * 0x10
obj["list_b2"] = [1] * 0x1_00_00

obj["str_b1"] = "a" * 0x20
obj["str_b2"] = "a" * 0x1_00
obj["str_b3"] = "a" * 0x1_00_00

obj["bytes_b1"] = b"a" * 0x1_00
obj["bytes_b2"] = b"a" * 0x1_00_00


obj_extra = {None: None, 3: 3, -1: -1, True: True, False: "hey", 1.1: 1.1}


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
