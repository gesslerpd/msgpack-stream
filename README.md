# msgpack-streams

Fast stream based implementation of msgpack in pure Python.

## Installation

```bash
pip install msgpack-streams
```

## Benchmarks

Average of 50 iterations each on a 3.77 MB payload, pure Python
(`MSGPACK_PUREPYTHON=1`).

| Implementation                  | Operation | Speedup vs msgpack |
| ------------------------------- | --------- | ------------------ |
| msgpack-streams `unpack`        | decode    | 2.83x              |
| msgpack-streams `unpack_stream` | decode    | 2.70x              |
| msgpack-streams `pack`          | encode    | 1.84x              |
| msgpack-streams `pack_stream`   | encode    | 1.69x              |

## Usage

```python
from msgpack_streams import pack, unpack

data = {"key": "value", "number": 42, "list": [1, 2, 3]}
packed = pack(data)
unpacked, excess_data = unpack(packed)
assert data == unpacked
assert not excess_data
```

The stream based API is also available:

```python
from msgpack_streams import pack_stream, unpack_stream
import io

data = {"key": "value", "number": 42, "list": [1, 2, 3]}

with io.BytesIO() as stream:
    pack_stream(stream, data)
    # reset stream position for reading
    stream.seek(0)
    unpacked = unpack_stream(stream)

assert data == unpacked
```

## Extensions

### Datetime

Timezone-aware `datetime` objects are natively supported and automatically
encoded using the
[msgpack Timestamp extension](https://github.com/msgpack/msgpack/blob/master/spec.md#timestamp-extension-type)
(type code `-1`). The timestamp format (32-, 64-, or 96-bit) is chosen
automatically based on the value's range and precision. Decoded timestamps are
always returned as UTC `datetime` objects.

```python
from datetime import datetime, timezone
from msgpack_streams import pack_stream, unpack_stream
import io

dt = datetime(2025, 3, 25, 12, 0, 0, tzinfo=timezone.utc)

with io.BytesIO() as stream:
    pack_stream(stream, dt)
    stream.seek(0)
    unpacked = unpack_stream(stream)

assert unpacked == dt
```

Naive `datetime` objects (without `tzinfo`) will raise a `ValueError`.

### ExtType

Arbitrary msgpack extension types are supported via the `ExtType` dataclass:

```python
from msgpack_streams import ExtType, pack_stream, unpack_stream
import io

obj = ExtType(code=42, data=b"hello")

with io.BytesIO() as stream:
    pack_stream(stream, obj)
    stream.seek(0)
    unpacked = unpack_stream(stream)

assert unpacked == obj
```

Use `ext_hook` to pack custom types as extensions, and `ext_hook` to decode them
back:

```python
from msgpack_streams import ExtType, pack, unpack
from fmtspec import decode, encode, types  # https://pypi.org/project/fmtspec/

class Point:
    EXT_CODE = 10

    __fmt__ = {
        "x": types.u32,
        "y": types.u32,
    }

    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

def unknown_type_hook(obj):
    if isinstance(obj, Point):
        return ExtType(Point.EXT_CODE, encode(obj))
    return None  # unsupported type → TypeError

def ext_hook(ext):
    if ext.code == Point.EXT_CODE:
        return decode(ext.data, shape=Point)
    return None  # unknown → keep as ExtType

pt = Point(1, 2)
packed = pack(pt, ext_hook=unknown_type_hook)
result, _ = unpack(packed, ext_hook=ext_hook)
assert result.x == pt.x and result.y == pt.y
```

## API reference

```python
def pack(obj: object, *, float32: bool = False, ext_hook: Callable[[object], ExtType | None] | None = None) -> bytes:
    ...
```

Serialize `obj` to a `bytes` object. Pass `float32=True` to encode `float`
values as 32-bit instead of the default 64-bit.

Pass `ext_hook` to handle types that are not natively supported. The callback
receives the unsupported object and should return an `ExtType` to pack in its
place. If it returns `None` a `TypeError` is raised as normal.

---

```python
def unpack(data: bytes, *, ext_hook: Callable[[ExtType], object | None] | None = None) -> tuple[object, bytes]:
    ...
```

Deserialize the first msgpack object from `data`. Returns `(obj, excess)` where
`excess` is any unconsumed bytes that followed the object.

Pass `ext_hook` to convert `ExtType` values during decoding. The callback
receives each `ExtType` and should return the decoded object, or `None` to leave
it as an `ExtType`.

---

```python
def pack_stream(stream: BinaryIO, obj: object, *, float32: bool = False, ext_hook: Callable[[object], ExtType | None] | None = None) -> None:
    ...
```

Serialize `obj` directly into a binary stream. Pass `float32=True` to encode
`float` values as 32-bit instead of the default 64-bit.

Pass `ext_hook` to handle types that are not natively supported. The callback
receives the unsupported object and should return an `ExtType` to pack in its
place. If it returns `None` a `TypeError` is raised as normal.

---

```python
def unpack_stream(stream: BinaryIO, *, ext_hook: Callable[[ExtType], object] | None = None) -> object:
    ...
```

Deserialize a single msgpack object from a binary stream, advancing the stream
position past the consumed bytes.

Pass `ext_hook` to convert `ExtType` values during decoding. The callback
receives each `ExtType` and should return the decoded object, or `None` to leave
it as an `ExtType`.
