import io
from msgpack_stream import pack_stream, unpack_stream, ExtType


def test_fixext1():
    stream = io.BytesIO()
    obj = ExtType(1, b"a")
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xd4"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_fixext2():
    stream = io.BytesIO()
    obj = ExtType(2, b"ab")
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xd5"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_fixext4():
    stream = io.BytesIO()
    obj = ExtType(3, b"abcd")
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xd6"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_fixext8():
    stream = io.BytesIO()
    obj = ExtType(4, b"a" * 8)
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xd7"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_fixext16():
    stream = io.BytesIO()
    obj = ExtType(5, b"a" * 16)
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xd8"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_ext8():
    stream = io.BytesIO()
    obj = ExtType(6, b"abc")
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xc7"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_ext16():
    stream = io.BytesIO()
    obj = ExtType(7, b"a" * 256)
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xc8"
    stream.seek(0)
    assert unpack_stream(stream) == obj


def test_ext32():
    stream = io.BytesIO()
    obj = ExtType(8, b"a" * 65536)
    pack_stream(stream, obj)
    stream.seek(0)
    assert stream.read(1) == b"\xc9"
    stream.seek(0)
    assert unpack_stream(stream) == obj
