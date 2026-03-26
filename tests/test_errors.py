"""Tests for error conditions in msgpack-streams to increase coverage."""

import io
from datetime import datetime
from unittest import mock

import pytest

from msgpack_streams import ExtType, pack_stream, unpack_stream


def test_int_too_large_negative():
    """Test that extremely large negative integers raise ValueError."""
    stream = io.BytesIO()
    # Larger than max int64
    obj = -(2**63 + 1)
    with pytest.raises(ValueError, match="int too large"):
        pack_stream(stream, obj)


def test_uint_too_large():
    """Test that extremely large unsigned integers raise ValueError."""
    stream = io.BytesIO()
    # Larger than max uint64
    obj = 2**64
    with pytest.raises(ValueError, match="uint too large"):
        pack_stream(stream, obj)


def test_str_too_large():
    """Test that strings exceeding max str32 length raise ValueError."""
    stream = io.BytesIO()
    test_str = "test"

    with mock.patch("msgpack_streams._msgpack.len", return_value=2**32) as patch:
        with pytest.raises(ValueError, match="str too large"):
            pack_stream(stream, test_str)
    patch.assert_called_once()


def test_bin_too_large():
    """Test that bytes exceeding max bin32 length raise ValueError."""
    stream = io.BytesIO()
    test_bytes = b"test"

    with mock.patch("msgpack_streams._msgpack.len", return_value=2**32) as patch:
        with pytest.raises(ValueError, match="bin too large"):
            pack_stream(stream, test_bytes)
    patch.assert_called_once()


def test_map_too_large():
    """Test that dicts exceeding max map32 length raise ValueError."""
    stream = io.BytesIO()
    test_dict = {"key": "value"}

    with mock.patch("msgpack_streams._msgpack.len", return_value=2**32) as patch:
        with pytest.raises(ValueError, match="map too large"):
            pack_stream(stream, test_dict)

    patch.assert_called_once()


def test_array_too_large():
    """Test that lists exceeding max array32 length raise ValueError."""
    stream = io.BytesIO()
    test_list = [1, 2, 3]

    with mock.patch("msgpack_streams._msgpack.len", return_value=2**32) as patch:
        with pytest.raises(ValueError, match="array too large"):
            pack_stream(stream, test_list)

    patch.assert_called_once()


def test_naive_datetime():
    """Test that naive datetime objects raise ValueError."""
    stream = io.BytesIO()
    dt = datetime(2023, 11, 19, 12, 0, 0)  # No timezone
    with pytest.raises(ValueError, match="timezone-aware"):
        pack_stream(stream, dt)


def test_ext_too_large():
    """Test that ExtType data exceeding max ext32 length raises ValueError."""
    stream = io.BytesIO()
    test_data = b"test"
    test_ext = ExtType(code=42, data=test_data)

    with mock.patch("msgpack_streams._msgpack.len", return_value=2**32) as patch:
        with pytest.raises(ValueError, match="ext too large"):
            pack_stream(stream, test_ext)

    patch.assert_called_once()


def test_unsupported_type():
    """Test that unsupported types raise TypeError."""
    stream = io.BytesIO()

    # Test with other unsupported types
    with pytest.raises(TypeError, match="unsupported type"):
        pack_stream(stream, set([1, 2, 3]))

    with pytest.raises(TypeError, match="unsupported type"):
        pack_stream(stream, frozenset([1, 2, 3]))

    with pytest.raises(TypeError, match="unsupported type"):
        pack_stream(stream, complex(1, 2))


def test_invalid_first_byte_0xc1():
    """Test that 0xC1 (never used) raises ValueError."""
    stream = io.BytesIO(b"\xc1")
    with pytest.raises(ValueError, match="invalid first byte"):
        unpack_stream(stream)


def test_invalid_timestamp96_length():
    """Test that timestamp96 with wrong length raises ValueError."""
    stream = io.BytesIO()
    # ext8 with code -1 (timestamp) but length != 4, 8, or 12
    # Format: 0xC7 (ext8), length, code (-1 = 0xFF), data
    stream.write(b"\xc7\x0d\xff" + b"\x00" * 13)  # 13 bytes instead of 12
    stream.seek(0)
    with pytest.raises(ValueError, match="invalid timestamp length"):
        unpack_stream(stream)


def test_invalid_fixext_timestamp_length():
    """Test that fixext timestamp with invalid length raises ValueError."""
    stream = io.BytesIO()
    # fixext2 with timestamp code should fail (only 4, 8 allowed for fixext)
    # Format: 0xD5 (fixext2), code (-1 = 0xFF), data
    stream.write(b"\xd5\xff\x00\x00")
    stream.seek(0)
    with pytest.raises(ValueError, match="invalid timestamp length"):
        unpack_stream(stream)


def test_unsupported_reserved_extension_ext8():
    """Test that reserved extensions other than timestamp raise NotImplementedError."""
    stream = io.BytesIO()
    # ext8 with code -2 (reserved but not timestamp)
    # Format: 0xC7 (ext8), length, code (-2 = 0xFE), data
    stream.write(b"\xc7\x04\xfe" + b"\x00" * 4)
    stream.seek(0)
    with pytest.raises(NotImplementedError, match="unsupported reserved extension"):
        unpack_stream(stream)


def test_unsupported_reserved_extension_fixext():
    """Test that fixext with reserved code (not timestamp) raises NotImplementedError."""
    stream = io.BytesIO()
    # fixext1 with code -2 (reserved but not timestamp)
    # Format: 0xD4 (fixext1), code (-2 = 0xFE), data
    stream.write(b"\xd4\xfe\x00")
    stream.seek(0)
    with pytest.raises(NotImplementedError, match="unsupported reserved extension"):
        unpack_stream(stream)


def test_invalid_first_byte():
    """Test that 0xC1 (never used) raises ValueError."""
    for i in range(2**8):
        if i == 0xC1:
            continue
        stream = io.BytesIO(bytes([i]))
        try:
            unpack_stream(stream)
        except ValueError:
            raise
        except Exception:
            pass
        else:
            pass
