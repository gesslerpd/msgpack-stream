"""Tests for ext_hook (unpack) and ext_hook (pack) callback features."""

import io

import pytest

from msgpack_streams import ExtType, pack, pack_stream, unpack, unpack_stream

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class Point:
    """Simple custom type used throughout the tests."""

    EXT_CODE = 10

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def to_ext(self) -> ExtType:
        return ExtType(self.EXT_CODE, self.x.to_bytes(4, "big") + self.y.to_bytes(4, "big"))

    @staticmethod
    def from_ext(ext: ExtType) -> "Point":
        x = int.from_bytes(ext.data[:4], "big")
        y = int.from_bytes(ext.data[4:], "big")
        return Point(x, y)


def point_pack_ext_hook(obj: object) -> ExtType | None:
    if isinstance(obj, Point):
        return obj.to_ext()
    return None


def point_ext_hook(ext: ExtType) -> object | None:
    if ext.code == Point.EXT_CODE:
        return Point.from_ext(ext)
    return None


# ---------------------------------------------------------------------------
# pack / ext_hook callback — pack_stream
# ---------------------------------------------------------------------------


def test_pack_stream_ext_hook_converts_custom_type():
    stream = io.BytesIO()
    p = Point(1, 2)
    pack_stream(stream, p, ext_hook=point_pack_ext_hook)
    stream.seek(0)
    result = unpack_stream(stream)
    assert result == ExtType(Point.EXT_CODE, p.to_ext().data)


def test_pack_stream_ext_hook_none_raises_type_error():
    stream = io.BytesIO()
    with pytest.raises(TypeError, match="unsupported type"):
        pack_stream(stream, Point(1, 2), ext_hook=lambda _: None)


def test_pack_stream_no_ext_hook_raises_type_error():
    stream = io.BytesIO()
    with pytest.raises(TypeError, match="unsupported type"):
        pack_stream(stream, Point(1, 2))


def test_pack_stream_ext_hook_only_called_for_unknown_types():
    called_with = []

    def hook(obj: object) -> ExtType | None:
        called_with.append(obj)
        return None

    stream = io.BytesIO()
    pack_stream(stream, 42, ext_hook=hook)
    assert called_with == [], "ext_hook should not be called for known types"


def test_pack_stream_ext_hook_nested_in_list():
    """ext_hook callback should propagate into nested structures (list)."""
    stream = io.BytesIO()
    pts = [Point(0, 0), Point(3, 4)]
    pack_stream(stream, pts, ext_hook=point_pack_ext_hook)
    stream.seek(0)
    result = unpack_stream(stream)
    assert result == [p.to_ext() for p in pts]


def test_pack_stream_ext_hook_nested_in_dict():
    """ext_hook callback should propagate into nested structures (dict)."""
    stream = io.BytesIO()
    obj = {"pt": Point(5, 6)}
    pack_stream(stream, obj, ext_hook=point_pack_ext_hook)
    stream.seek(0)
    result = unpack_stream(stream)
    assert result == {"pt": Point(5, 6).to_ext()}


# ---------------------------------------------------------------------------
# pack / ext_hook callback — high-level pack()
# ---------------------------------------------------------------------------


def test_pack_unknown_hook_converts_custom_type():
    p = Point(7, 8)
    data = pack(p, ext_hook=point_pack_ext_hook)
    obj, excess = unpack(data)
    assert obj == p.to_ext()
    assert not excess


def test_pack_unknown_hook_none_raises_type_error():
    with pytest.raises(TypeError, match="unsupported type"):
        pack(Point(1, 2), ext_hook=lambda _: None)


def test_pack_no_unknown_hook_raises_type_error():
    with pytest.raises(TypeError, match="unsupported type"):
        pack(Point(1, 2))


# ---------------------------------------------------------------------------
# unpack / ext_hook callback — unpack_stream
# ---------------------------------------------------------------------------


def test_unpack_stream_ext_hook_converts_ext():
    stream = io.BytesIO()
    p = Point(10, 20)
    pack_stream(stream, p.to_ext())
    stream.seek(0)
    result = unpack_stream(stream, ext_hook=point_ext_hook)
    assert result == p


def test_unpack_stream_ext_hook_returns_none_keeps_ext():
    """ext_hook returning None should leave the value as ExtType."""
    stream = io.BytesIO()
    ext = ExtType(99, b"raw")
    pack_stream(stream, ext)
    stream.seek(0)
    result = unpack_stream(stream, ext_hook=lambda _: None)
    assert result == ext


def test_unpack_stream_no_ext_hook_returns_ext_type():
    stream = io.BytesIO()
    ext = ExtType(5, b"hello")
    pack_stream(stream, ext)
    stream.seek(0)
    result = unpack_stream(stream)
    assert result == ext


def test_unpack_stream_ext_hook_unknown_code_falls_back():
    """ext_hook can selectively convert; unknown codes get ExtType."""
    stream = io.BytesIO()
    ext = ExtType(77, b"data")
    pack_stream(stream, ext)
    stream.seek(0)
    result = unpack_stream(stream, ext_hook=point_ext_hook)  # code != 10
    assert result == ext


def test_unpack_stream_ext_hook_fixext_formats():
    """ext_hook fires for all fixext sizes (0xD4–0xD8)."""
    for size in (1, 2, 4, 8, 16):
        data = b"x" * size
        ext = ExtType(Point.EXT_CODE, data)
        stream = io.BytesIO()
        pack_stream(stream, ext)
        stream.seek(0)
        seen: list[ExtType] = []

        def hook(e: ExtType, _seen=seen) -> object | None:
            _seen.append(e)
            return None

        unpack_stream(stream, ext_hook=hook)
        assert seen == [ext]


def test_unpack_stream_ext_hook_ext8_ext16_ext32_formats():
    """ext_hook fires for ext8, ext16, ext32 formats."""
    for size in (3, 256, 65536):
        data = b"a" * size
        ext = ExtType(Point.EXT_CODE, data)
        stream = io.BytesIO()
        pack_stream(stream, ext)
        stream.seek(0)
        seen: list[ExtType] = []

        def hook(e: ExtType, _seen=seen) -> object | None:
            _seen.append(e)
            return None

        unpack_stream(stream, ext_hook=hook)
        assert seen == [ext]


def test_unpack_stream_ext_hook_nested_in_list():
    """ext_hook propagates into nested list values."""
    pts = [Point(1, 2), Point(3, 4)]
    stream = io.BytesIO()
    pack_stream(stream, [p.to_ext() for p in pts])
    stream.seek(0)
    result = unpack_stream(stream, ext_hook=point_ext_hook)
    assert result == pts


def test_unpack_stream_ext_hook_nested_in_dict():
    """ext_hook propagates into nested dict values."""
    p = Point(5, 6)
    stream = io.BytesIO()
    pack_stream(stream, {"pt": p.to_ext()})
    stream.seek(0)
    result = unpack_stream(stream, ext_hook=point_ext_hook)
    assert result == {"pt": p}


# ---------------------------------------------------------------------------
# unpack / ext_hook callback — high-level unpack()
# ---------------------------------------------------------------------------


def test_unpack_ext_hook_converts_ext():
    p = Point(30, 40)
    data = pack(p.to_ext())
    obj, excess = unpack(data, ext_hook=point_ext_hook)
    assert obj == p
    assert not excess


def test_unpack_ext_hook_none_keeps_ext_type():
    ext = ExtType(99, b"raw")
    data = pack(ext)
    obj, excess = unpack(data, ext_hook=lambda e: None)
    assert obj == ext
    assert not excess


# ---------------------------------------------------------------------------
# Round-trip: pack with default then unpack with ext_hook
# ---------------------------------------------------------------------------


def test_roundtrip_pack_unknown_hook_unpack_ext_hook():
    p = Point(100, 200)
    data = pack(p, ext_hook=point_pack_ext_hook)
    obj, excess = unpack(data, ext_hook=point_ext_hook)
    assert obj == p
    assert not excess


def test_roundtrip_nested_list():
    pts = [Point(i, i * 2) for i in range(5)]
    data = pack(pts, ext_hook=point_pack_ext_hook)
    result, excess = unpack(data, ext_hook=point_ext_hook)
    assert result == pts
    assert not excess


def test_roundtrip_nested_dict():
    obj = {"a": Point(1, 1), "b": [Point(2, 3), Point(4, 5)]}
    data = pack(obj, ext_hook=point_pack_ext_hook)
    result, excess = unpack(data, ext_hook=point_ext_hook)
    assert result == obj
    assert not excess
