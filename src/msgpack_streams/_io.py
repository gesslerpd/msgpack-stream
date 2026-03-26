from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

from ._ext import ExtType
from ._msgpack import pack_stream, unpack_stream


def pack(
    obj: object,
    *,
    float32: bool = False,
    ext_hook: Callable[[object], ExtType | Any] | None = None,
) -> bytes:
    """Pack object into data."""
    with io.BytesIO() as stream:
        pack_stream(stream, obj, float32=float32, ext_hook=ext_hook)
        data = stream.getvalue()
    return data


def unpack(
    data: bytes,
    *,
    ext_hook: Callable[[ExtType], object] | None = None,
) -> tuple[object, bytes]:
    """Unpack data into object."""
    with io.BytesIO(data) as stream:
        obj = unpack_stream(stream, ext_hook=ext_hook)
        excess_data = stream.read()
    return obj, excess_data
