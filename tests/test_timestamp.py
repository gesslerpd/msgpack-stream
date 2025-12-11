import io
from datetime import datetime, timedelta, timezone

import pytest

from msgpack_stream import pack_stream, unpack_stream


def roundtrip(obj):
    stream = io.BytesIO()
    pack_stream(stream, obj)
    stream.seek(0)
    return unpack_stream(stream)


def test_timestamp_32():
    # 2023-11-19 12:00:00 UTC
    dt = datetime(2023, 11, 19, 12, 0, 0, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt

    # Epoch
    dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt


def test_timestamp_64():
    # 2023-11-19 12:00:00.123456 UTC
    dt = datetime(2023, 11, 19, 12, 0, 0, 123456, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt

    # Max timestamp 32 + 1 second
    dt = datetime(2106, 2, 7, 6, 28, 16, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt


def test_timestamp_96():
    # Very far future
    dt = datetime(3000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt

    # Before epoch
    dt = datetime(1969, 12, 31, 13, 20, 20, 333333, tzinfo=timezone.utc)
    assert roundtrip(dt) == dt


def test_naive_datetime_error():
    dt = datetime(2023, 11, 19, 12, 0, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        roundtrip(dt)


def test_timezone_conversion():
    # EST is UTC-5
    tz = timezone(timedelta(hours=-5))
    dt = datetime(2023, 11, 19, 12, 0, 0, 999999, tzinfo=tz)
    unpacked = roundtrip(dt)
    assert unpacked.tzinfo == timezone.utc
    assert unpacked == dt
    assert unpacked.astimezone(tz) == dt
