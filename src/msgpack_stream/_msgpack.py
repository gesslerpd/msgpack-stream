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

_B = tuple([bytes([i]) for i in range(256)])


def pack_stream(stream, obj):
    _ps = pack_stream
    _b = _B
    _write = stream.write
    _type = type(obj)
    if _type is int:
        i = obj
        if 0 <= i <= 0x7F:  # positive fixint
            _write(_b[i])
        elif -32 <= i < 0:  # negative fixint
            _write(_b[i & 0xFF])
        elif i < 0:  # wider negative
            ai = -i
            if ai <= 0x80:
                _write(b"\xd0")
                s8_b_pack(stream, i)
            elif ai <= 0x80_00:
                _write(b"\xd1")
                s16_b_pack(stream, i)
            elif ai <= 0x80_00_00_00:
                _write(b"\xd2")
                s32_b_pack(stream, i)
            elif ai <= 0x80_00_00_00_00_00_00_00:
                _write(b"\xd3")
                s64_b_pack(stream, i)
            else:
                raise ValueError("int too large")
        elif i <= 0xFF:
            _write(b"\xcc")
            u8_b_pack(stream, i)
        elif i <= 0xFF_FF:
            _write(b"\xcd")
            u16_b_pack(stream, i)
        elif i <= 0xFF_FF_FF_FF:
            _write(b"\xce")
            u32_b_pack(stream, i)
        elif i <= 0xFF_FF_FF_FF_FF_FF_FF_FF:
            _write(b"\xcf")
            u64_b_pack(stream, i)
        else:
            raise ValueError("uint too large")
    elif _type is float:
        _write(b"\xcb")
        f64_b_pack(stream, obj)
    elif _type is dict:
        map_length = len(obj)
        if map_length <= 0x0F:
            _write(_b[0x80 | map_length])
        elif map_length <= 0xFF_FF:
            _write(b"\xde")
            u16_b_pack(stream, map_length)
        elif map_length <= 0xFF_FF_FF_FF:
            _write(b"\xdf")
            u32_b_pack(stream, map_length)
        else:
            raise ValueError("map too large", obj)
        for k, v in obj.items():
            _ps(stream, k)
            _ps(stream, v)
    elif _type is list:
        array_length = len(obj)
        if array_length <= 0x0F:
            _write(_b[0x90 | array_length])
        elif array_length <= 0xFF_FF:
            _write(b"\xdc")
            u16_b_pack(stream, array_length)
        elif array_length <= 0xFF_FF_FF_FF:
            _write(b"\xdd")
            u32_b_pack(stream, array_length)
        else:
            raise ValueError("array too large", obj)
        for v in obj:
            _ps(stream, v)
    elif _type is str:
        s = obj.encode("utf-8")
        sl = len(s)
        if sl <= 0x1F:
            _write(_b[0xA0 | sl])
        elif sl <= 0xFF:
            _write(b"\xd9")
        elif sl <= 0xFF_FF:
            _write(b"\xda")
        elif sl <= 0xFF_FF_FF_FF:
            _write(b"\xdb")
        else:
            raise ValueError("str too large", obj)
        _write(s)
    elif obj is None:
        _write(b"\xc0")
    elif _type is bool:
        _write(b"\xc3" if obj else b"\xc2")
    elif _type is bytes:
        bin_length = len(obj)
        if bin_length <= 0xFF:
            _write(b"\xc4")
            u8_b_pack(stream, bin_length)
        elif bin_length <= 0xFF_FF:
            _write(b"\xc5")
            u16_b_pack(stream, bin_length)
        elif bin_length <= 0xFF_FF_FF_FF:
            _write(b"\xc6")
            u32_b_pack(stream, bin_length)
        else:
            raise ValueError("bin too large", obj)
        _write(obj)
    else:
        raise TypeError("type not supported:", obj, type(obj))


def unpack_stream(stream):
    b = stream.read(1)
    first_byte = b[0]
    if first_byte <= 0x7F:  # positive fixint
        return first_byte
    if first_byte >= 0xE0:  # negative fixint
        return first_byte - 0x100
    if first_byte <= 0x8F:  # fixmap
        mlen = first_byte & 0x0F
        return {unpack_stream(stream): unpack_stream(stream) for _ in range(mlen)}
    if first_byte <= 0x9F:  # fixarray
        alen = first_byte & 0x0F
        return [unpack_stream(stream) for _ in range(alen)]
    if first_byte <= 0xBF:  # fixstr
        slen = first_byte & 0x1F
        return stream.read(slen).decode("utf-8")
    if first_byte == 0xC0:
        return None
    if first_byte == 0xC2:
        return False
    if first_byte == 0xC3:
        return True
    if first_byte == 0xC4:
        bl = u8_b_unpack(stream)
        return stream.read(bl)
    if first_byte == 0xC5:
        bl = u16_b_unpack(stream)
        return stream.read(bl)
    if first_byte == 0xC6:
        bl = u32_b_unpack(stream)
        return stream.read(bl)
    if 0xC7 <= first_byte <= 0xC9:
        raise NotImplementedError
    if first_byte == 0xCA:
        return f32_b_unpack(stream)
    if first_byte == 0xCB:
        return f64_b_unpack(stream)
    if first_byte == 0xCC:
        return u8_b_unpack(stream)
    if first_byte == 0xCD:
        return u16_b_unpack(stream)
    if first_byte == 0xCE:
        return u32_b_unpack(stream)
    if first_byte == 0xCF:
        return u64_b_unpack(stream)
    if first_byte == 0xD0:
        return s8_b_unpack(stream)
    if first_byte == 0xD1:
        return s16_b_unpack(stream)
    if first_byte == 0xD2:
        return s32_b_unpack(stream)
    if first_byte == 0xD3:
        return s64_b_unpack(stream)
    if 0xD4 <= first_byte <= 0xD8:
        raise NotImplementedError
    if first_byte == 0xD9:
        sl = u8_b_unpack(stream)
        return stream.read(sl).decode("utf-8")
    if first_byte == 0xDA:
        sl = u16_b_unpack(stream)
        return stream.read(sl).decode("utf-8")
    if first_byte == 0xDB:
        sl = u32_b_unpack(stream)
        return stream.read(sl).decode("utf-8")
    if first_byte == 0xDC:
        al = u16_b_unpack(stream)
        return [unpack_stream(stream) for _ in range(al)]
    if first_byte == 0xDD:
        al = u32_b_unpack(stream)
        return [unpack_stream(stream) for _ in range(al)]
    if first_byte == 0xDE:
        ml = u16_b_unpack(stream)
        return {unpack_stream(stream): unpack_stream(stream) for _ in range(ml)}
    if first_byte == 0xDF:
        ml = u32_b_unpack(stream)
        return {unpack_stream(stream): unpack_stream(stream) for _ in range(ml)}
    raise ValueError("invalid first byte", first_byte, hex(first_byte))
