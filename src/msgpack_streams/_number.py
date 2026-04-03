from __future__ import annotations

import struct
from typing import BinaryIO, Generic, TypeVar

T = TypeVar("T", int, float)


class Number(Generic[T]):
    __slots__ = ("struct",)

    def __init__(self, fmt: str) -> None:
        self.struct = struct.Struct(fmt)

    def pack(self, stream: BinaryIO, obj: T) -> None:
        data = self.struct.pack(obj)
        stream.write(data)

    def unpack(self, stream: BinaryIO) -> T:
        data = stream.read(self.struct.size)
        (obj,) = self.struct.unpack(data)
        return obj


# u8_t = Number[int]("<B")
# u16_t = Number[int]("<H")
# u32_t = Number[int]("<I")
# u64_t = Number[int]("<Q")

u8_b_t = Number[int](">B")
u16_b_t = Number[int](">H")
u32_b_t = Number[int](">I")
u64_b_t = Number[int](">Q")

# s8_t = Number[int]("<b")
# s16_t = Number[int]("<h")
# s32_t = Number[int]("<i")
# s64_t = Number[int]("<q")

s8_b_t = Number[int](">b")
s16_b_t = Number[int](">h")
s32_b_t = Number[int](">i")
s64_b_t = Number[int](">q")

# f16_t = Number[float]("<e")
# f32_t = Number[float]("<f")
# f64_t = Number[float]("<d")

# f16_b_t = Number[float](">e")
f32_b_t = Number[float](">f")
f64_b_t = Number[float](">d")
