import struct


class Number:
    __slots__ = ["struct"]

    def __init__(self, fmt):
        self.struct = struct.Struct(fmt)

    def pack(self, stream, obj):
        data = self.struct.pack(obj)
        stream.write(data)

    def unpack(self, stream):
        data = stream.read(self.struct.size)
        (obj,) = self.struct.unpack(data)
        return obj


# u8_t = Number("<B")
# u16_t = Number("<H")
# u32_t = Number("<I")
# u64_t = Number("<Q")

u8_b_t = Number(">B")
u16_b_t = Number(">H")
u32_b_t = Number(">I")
u64_b_t = Number(">Q")

# s8_t = Number("<b")
# s16_t = Number("<h")
# s32_t = Number("<i")
# s64_t = Number("<q")

s8_b_t = Number(">b")
s16_b_t = Number(">h")
s32_b_t = Number(">i")
s64_b_t = Number(">q")

# f16_t = Number("<e")
# f32_t = Number("<f")
# f64_t = Number("<d")

# f16_b_t = Number(">e")
f32_b_t = Number(">f")
f64_b_t = Number(">d")
