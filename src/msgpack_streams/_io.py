from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

from ._ext import ExtType
from ._msgpack import _pack_stream, _unpack_stream


def pack(
    obj: object,
    *,
    float32: bool = False,
    ext_hook: Callable[[object], ExtType | Any] | None = None,
    max_depth: int = -1,
) -> bytes:
    """Pack object into data."""
    with io.BytesIO() as stream:
        _pack_stream(stream, obj, float32, ext_hook, max_depth)
        data = stream.getvalue()
    return data


def unpack(
    data: bytes,
    *,
    ext_hook: Callable[[ExtType], object] | None = None,
    max_depth: int = -1,
) -> tuple[object, bytes]:
    """Unpack object from data."""
    with io.BytesIO(data) as stream:
        obj = _unpack_stream(stream, ext_hook, max_depth)
        excess_data = stream.read()
    return obj, excess_data
