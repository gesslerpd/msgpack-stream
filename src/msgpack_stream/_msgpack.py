from ._number import (
    u8_b_t,
    u16_b_t,
    u32_b_t,
    u64_b_t,
    s8_b_t,
    s16_b_t,
    s32_b_t,
    s64_b_t,
    f32_b_t,
    f64_b_t,
)

# deference for performance
u8_b_pack = u8_b_t.pack
u16_b_pack = u16_b_t.pack
u32_b_pack = u32_b_t.pack
u64_b_pack = u64_b_t.pack
s8_b_pack = s8_b_t.pack
s16_b_pack = s16_b_t.pack
s32_b_pack = s32_b_t.pack
s64_b_pack = s64_b_t.pack
f32_b_pack = f32_b_t.pack
f64_b_pack = f64_b_t.pack

u8_b_unpack = u8_b_t.unpack
u16_b_unpack = u16_b_t.unpack
u32_b_unpack = u32_b_t.unpack
u64_b_unpack = u64_b_t.unpack
s8_b_unpack = s8_b_t.unpack
s16_b_unpack = s16_b_t.unpack
s32_b_unpack = s32_b_t.unpack
s64_b_unpack = s64_b_t.unpack
f32_b_unpack = f32_b_t.unpack
f64_b_unpack = f64_b_t.unpack


def pack_stream(stream, obj):
    if isinstance(obj, dict):
        map_length = len(obj)
        if map_length <= 0x0F:
            u8_b_pack(stream, 0b10000000 + map_length)
        elif map_length <= 0xFF_FF:
            stream.write(b"\xde")
            u16_b_pack(stream, map_length)
        elif map_length <= 0xFF_FF_FF_FF:
            stream.write(b"\xdf")
            u32_b_pack(stream, map_length)
        else:
            raise ValueError("map too large", obj)
        for key, value in obj.items():
            pack_stream(stream, key)
            pack_stream(stream, value)
    elif isinstance(obj, bool):
        stream.write(b"\xc3" if obj else b"\xc2")
    elif isinstance(obj, int):
        int_negative = obj < 0
        int_abs = abs(obj)
        if int_negative:
            if int_abs <= 0b100000:
                s8_b_pack(stream, obj)
            elif int_abs <= 0x80:
                stream.write(b"\xd0")
                s8_b_pack(stream, obj)
            elif int_abs <= 0x80_00:
                stream.write(b"\xd1")
                s16_b_pack(stream, obj)
            elif int_abs <= 0x80_00_00_00:
                stream.write(b"\xd2")
                s32_b_pack(stream, obj)
            elif int_abs <= 0x80_00_00_00_00_00_00_00:
                stream.write(b"\xd3")
                s64_b_pack(stream, obj)
            else:
                raise ValueError("int too large")
        else:
            if int_abs <= 0b1111111:
                u8_b_pack(stream, obj)
            elif int_abs <= 0xFF:
                stream.write(b"\xcc")
                u8_b_pack(stream, obj)
            elif int_abs <= 0xFF_FF:
                stream.write(b"\xcd")
                u16_b_pack(stream, obj)
            elif int_abs <= 0xFF_FF_FF_FF:
                stream.write(b"\xce")
                u32_b_pack(stream, obj)
            elif int_abs <= 0xFF_FF_FF_FF_FF_FF_FF_FF:
                stream.write(b"\xcf")
                u64_b_pack(stream, obj)
            else:
                raise ValueError("uint too large")
    elif isinstance(obj, float):
        stream.write(b"\xcb")
        f64_b_pack(stream, obj)
    elif isinstance(obj, (bytes, bytearray)):
        bin_length = len(obj)
        if bin_length <= 0xFF:
            stream.write(b"\xc4")
            u8_b_pack(stream, bin_length)
        elif bin_length <= 0xFF_FF:
            stream.write(b"\xc5")
            u16_b_pack(stream, bin_length)
        elif bin_length <= 0xFF_FF_FF_FF:
            stream.write(b"\xc6")
            u32_b_pack(stream, bin_length)
        else:
            raise ValueError("bin too large", obj)
        stream.write(obj)
    elif isinstance(obj, str):
        str_bytes = obj.encode("utf-8")
        str_length = len(str_bytes)
        if str_length <= 0b11111:
            u8_b_pack(stream, 0b10100000 + str_length)
        elif str_length <= 0xFF:
            stream.write(b"\xd9")
        elif str_length <= 0xFF_FF:
            stream.write(b"\xda")
        elif str_length <= 0xFF_FF_FF_FF:
            stream.write(b"\xdb")
        else:
            raise ValueError("str too large", obj)
        stream.write(str_bytes)
    elif isinstance(obj, list):
        array_length = len(obj)
        if array_length <= 0x0F:
            u8_b_pack(stream, 0b10010000 + array_length)
        elif array_length <= 0xFF_FF:
            stream.write(b"\xdc")
            u16_b_pack(stream, array_length)
        elif array_length <= 0xFF_FF_FF_FF:
            stream.write(b"\xdd")
            u32_b_pack(stream, array_length)
        else:
            raise ValueError("array too large", obj)
        for value in obj:
            pack_stream(stream, value)
    elif obj is None:
        stream.write(b"\xc0")
    else:
        raise TypeError("type not supported:", obj, type(obj))


def unpack_stream(stream):
    first_byte = u8_b_unpack(stream)
    if first_byte <= 0x7F:
        obj = first_byte
    elif first_byte <= 0x8F:
        map_length = first_byte & 0b1111
        obj = {unpack_stream(stream): unpack_stream(stream) for _ in range(map_length)}
    elif first_byte <= 0x9F:
        array_length = first_byte & 0b1111
        obj = [unpack_stream(stream) for _ in range(array_length)]
    elif first_byte <= 0xBF:
        str_length = first_byte & 0b11111
        obj = stream.read(str_length).decode("utf-8")
    elif 0xE0 <= first_byte and first_byte <= 0xFF:
        stream.seek(-1, 1)
        obj = s8_b_unpack(stream)
    elif first_byte == 0xC0:
        obj = None
    elif first_byte == 0xC2:
        obj = False
    elif first_byte == 0xC3:
        obj = True
    elif first_byte == 0xC4:
        bin_length = u8_b_unpack(stream)
        obj = stream.read(bin_length)
    elif first_byte == 0xC5:
        bin_length = u16_b_unpack(stream)
        obj = stream.read(bin_length)
    elif first_byte == 0xC6:
        bin_length = u32_b_unpack(stream)
        obj = stream.read(bin_length)
    elif first_byte == 0xC7:
        raise NotImplementedError
    elif first_byte == 0xC8:
        raise NotImplementedError
    elif first_byte == 0xC9:
        raise NotImplementedError
    elif first_byte == 0xCA:
        obj = f32_b_unpack(stream)
    elif first_byte == 0xCB:
        obj = f64_b_unpack(stream)
    elif first_byte == 0xCC:
        obj = u8_b_unpack(stream)
    elif first_byte == 0xCD:
        obj = u16_b_unpack(stream)
    elif first_byte == 0xCE:
        obj = u32_b_unpack(stream)
    elif first_byte == 0xCF:
        obj = u64_b_unpack(stream)
    elif first_byte == 0xD0:
        obj = s8_b_unpack(stream)
    elif first_byte == 0xD1:
        obj = s16_b_unpack(stream)
    elif first_byte == 0xD2:
        obj = s32_b_unpack(stream)
    elif first_byte == 0xD3:
        obj = s64_b_unpack(stream)
    elif first_byte == 0xD4:
        raise NotImplementedError
    elif first_byte == 0xD5:
        raise NotImplementedError
    elif first_byte == 0xD6:
        raise NotImplementedError
    elif first_byte == 0xD7:
        raise NotImplementedError
    elif first_byte == 0xD8:
        raise NotImplementedError
    elif first_byte == 0xD9:
        str_length = u8_b_unpack(stream)
        obj = stream.read(str_length).decode("utf-8")
    elif first_byte == 0xDA:
        str_length = u16_b_unpack(stream)
        obj = stream.read(str_length).decode("utf-8")
    elif first_byte == 0xDB:
        str_length = u32_b_unpack(stream)
        obj = stream.read(str_length).decode("utf-8")
    elif first_byte == 0xDC:
        array_length = u16_b_unpack(stream)
        obj = [unpack_stream(stream) for _ in range(array_length)]
    elif first_byte == 0xDD:
        array_length = u32_b_unpack(stream)
        obj = [unpack_stream(stream) for _ in range(array_length)]
    elif first_byte == 0xDE:
        map_length = u16_b_unpack(stream)
        obj = {unpack_stream(stream): unpack_stream(stream) for _ in range(map_length)}
    elif first_byte == 0xDF:
        map_length = u32_b_unpack(stream)
        obj = {unpack_stream(stream): unpack_stream(stream) for _ in range(map_length)}
    else:
        raise ValueError("invalid first byte", first_byte, hex(first_byte))

    return obj
