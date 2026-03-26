import io
import struct

import pytest

from msgpack_streams import pack, pack_stream, unpack, unpack_stream

# float32 format byte: 0xCA; float64 format byte: 0xCB
FLOAT32_MARKER = b"\xca"
FLOAT64_MARKER = b"\xcb"


def test_pack_default_is_float64():
    data = pack(1.5)
    assert data[:1] == FLOAT64_MARKER
    assert len(data) == 9  # 1 marker + 8 bytes


def test_pack_float32_option():
    data = pack(1.5, float32=True)
    assert data[:1] == FLOAT32_MARKER
    assert len(data) == 5  # 1 marker + 4 bytes


def test_pack_float32_raw_bytes():
    data = pack(1.5, float32=True)
    assert data[1:] == struct.pack(">f", 1.5)


def test_pack_float32_precision_loss():
    value = 3.141592653589793
    result32, _ = unpack(pack(value, float32=True))
    result64, _ = unpack(pack(value))
    assert result32 != result64
    assert result64 == value


def test_pack_stream_float32():
    stream = io.BytesIO()
    pack_stream(stream, 1.5, float32=True)
    assert stream.getvalue()[:1] == FLOAT32_MARKER


def test_deeply_nested_float32():
    obj = {"a": {"b": [1.0, {"c": 3.14}]}}
    data = pack(obj, float32=True)
    assert FLOAT64_MARKER not in data
    result, _ = unpack(data)
    assert result["a"]["b"][0] == pytest.approx(1.0)
    assert result["a"]["b"][1]["c"] == pytest.approx(3.14, rel=1e-5)


def test_non_float_unaffected_by_float32():
    obj = {"int": 42, "str": "hello", "bytes": b"\x00", "bool": True, "none": None}
    assert pack(obj, float32=True) == pack(obj)


def test_float32_nan():
    result, _ = unpack(pack(float("nan"), float32=True))
    assert result != result  # NaN != NaN
