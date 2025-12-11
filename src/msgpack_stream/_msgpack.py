import os
from datetime import datetime, timezone
from math import floor

from ._ext import ExtType
from ._number import (
    f32_b_t,
    f64_b_t,
    s8_b_t,
    s16_b_t,
    s32_b_t,
    s64_b_t,
    u8_b_t,
    u16_b_t,
    u32_b_t,
    u64_b_t,
)

# deference for performance

# u8_b_st = u8_b_t.struct
u16_b_st = u16_b_t.struct
u32_b_st = u32_b_t.struct
u64_b_st = u64_b_t.struct
s8_b_st = s8_b_t.struct
s16_b_st = s16_b_t.struct
s32_b_st = s32_b_t.struct
s64_b_st = s64_b_t.struct
f_b_st = f64_b_t.struct

if os.environ.get("MSGPACK_PACK_FLOAT32"):
    f_b_st = f32_b_t.struct

# u8_b_pack = u8_b_st.pack
u16_b_pack = u16_b_st.pack
u32_b_pack = u32_b_st.pack
u64_b_pack = u64_b_st.pack
s8_b_pack = s8_b_st.pack
s16_b_pack = s16_b_st.pack
s32_b_pack = s32_b_st.pack
s64_b_pack = s64_b_st.pack
f_b_pack = f_b_st.pack

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
_PO2 = {1: b"\xd4", 2: b"\xd5", 4: b"\xd6", 8: b"\xd7", 16: b"\xd8"}


# region: timestamp support
_NS_MASK = 0x3_FF_FF_FF_FF
_NS_MASK_LEN = 34


def _timestamp_to_datetime(seconds, nanoseconds):
    # python only supports microsecond precision
    return datetime.fromtimestamp(seconds + (nanoseconds / 1_000_000_000), timezone.utc)


# endregion


def pack_stream(stream, obj):
    _type = type(obj)
    if _type is int:  # int
        i = obj
        if 0 <= i <= 0x7F:  # positive fixint
            stream.write(_B[i])
        elif -32 <= i < 0:  # negative fixint
            stream.write(_B[i & 0xFF])
        elif i < 0:  # wider negative
            u_i = -i
            if u_i <= 0x80:  # int8
                stream.write(b"\xd0" + s8_b_pack(i))
            elif u_i <= 0x80_00:  # int16
                stream.write(b"\xd1" + s16_b_pack(i))
            elif u_i <= 0x80_00_00_00:  # int32
                stream.write(b"\xd2" + s32_b_pack(i))
            elif u_i <= 0x80_00_00_00_00_00_00_00:  # int64
                stream.write(b"\xd3" + s64_b_pack(i))
            else:
                raise ValueError("int too large", obj)
        elif i <= 0xFF:  # uint8
            stream.write(b"\xcc" + _B[i])
        elif i <= 0xFF_FF:  # uint16
            stream.write(b"\xcd" + u16_b_pack(i))
        elif i <= 0xFF_FF_FF_FF:  # uint32
            stream.write(b"\xce" + u32_b_pack(i))
        elif i <= 0xFF_FF_FF_FF_FF_FF_FF_FF:  # uint64
            stream.write(b"\xcf" + u64_b_pack(i))
        else:
            raise ValueError("uint too large", obj)
    elif _type is float:  # float32 / float64 (depends on MSGPACK_PACK_FLOAT32)
        stream.write(b"\xcb" + f_b_pack(obj))
    elif obj is None:  # nil
        stream.write(b"\xc0")
    elif _type is bool:  # true / false
        stream.write(b"\xc3" if obj else b"\xc2")
    elif _type is str:  # str
        s = obj.encode("utf-8")
        sl = len(s)
        if sl <= 0x1F:  # fixstr
            stream.write(_B[0xA0 | sl])
        elif sl <= 0xFF:  # str8
            stream.write(b"\xd9" + _B[sl])
        elif sl <= 0xFF_FF:  # str16
            stream.write(b"\xda" + u16_b_pack(sl))
        elif sl <= 0xFF_FF_FF_FF:  # str32
            stream.write(b"\xdb" + u32_b_pack(sl))
        else:
            raise ValueError("str too large", obj)
        stream.write(s)
    elif _type is bytes:  # bin
        bl = len(obj)
        if bl <= 0xFF:  # bin8
            stream.write(b"\xc4" + _B[bl])
        elif bl <= 0xFF_FF:  # bin16
            stream.write(b"\xc5" + u16_b_pack(bl))
        elif bl <= 0xFF_FF_FF_FF:  # bin32
            stream.write(b"\xc6" + u32_b_pack(bl))
        else:
            raise ValueError("bin too large", obj)
        stream.write(obj)
    elif _type is dict:  # map
        ml = len(obj)
        if ml <= 0x0F:  # fixmap
            stream.write(_B[0x80 | ml])
        elif ml <= 0xFF_FF:  # map16
            stream.write(b"\xde" + u16_b_pack(ml))
        elif ml <= 0xFF_FF_FF_FF:  # map32
            stream.write(b"\xdf" + u32_b_pack(ml))
        else:
            raise ValueError("map too large", obj)
        for k, v in obj.items():
            pack_stream(stream, k)
            pack_stream(stream, v)
    elif _type is list:  # array
        al = len(obj)
        if al <= 0x0F:  # fixarray
            stream.write(_B[0x90 | al])
        elif al <= 0xFF_FF:  # array16
            stream.write(b"\xdc" + u16_b_pack(al))
        elif al <= 0xFF_FF_FF_FF:  # array32
            stream.write(b"\xdd" + u32_b_pack(al))
        else:
            raise ValueError("array too large", obj)
        for v in obj:
            pack_stream(stream, v)
    elif _type is datetime:  # timestamp
        if obj.tzinfo is None:
            raise ValueError("datetime object must be timezone-aware", obj)

        seconds_from_epoch = obj.timestamp()
        # floor rather than int (handles negative timestamps correctly)
        seconds = floor(seconds_from_epoch)
        nanoseconds = int((seconds_from_epoch - seconds) * 1_000_000_000)

        if seconds >> _NS_MASK_LEN == 0:
            data64 = (nanoseconds << _NS_MASK_LEN) | seconds
            if data64 <= 0xFF_FF_FF_FF:
                # timestamp32
                stream.write(b"\xd6\xff" + u32_b_pack(data64))
            else:
                # timestamp64
                stream.write(b"\xd7\xff" + u64_b_pack(data64))
        else:
            # timestamp96
            stream.write(
                b"\xc7\x0c\xff" + u32_b_pack(nanoseconds) + s64_b_pack(seconds)
            )
    elif _type is ExtType:  # ext
        data = obj.data
        p_code = s8_b_pack(obj.code)
        extl = len(data)
        if extl <= 16 and extl in _PO2:  # fixext (0xD4 - 0xD8)
            stream.write(_PO2[extl] + p_code)
        elif extl <= 0xFF:  # ext8
            stream.write(b"\xc7" + _B[extl] + p_code)
        elif extl <= 0xFF_FF:  # ext16
            stream.write(b"\xc8" + u16_b_pack(extl) + p_code)
        elif extl <= 0xFF_FF_FF_FF:  # ext32
            stream.write(b"\xc9" + u32_b_pack(extl) + p_code)
        else:
            raise ValueError("ext too large", obj)
        stream.write(data)
    else:
        raise TypeError("unsupported type", _type, obj)


def unpack_stream(stream):
    b = stream.read(1)
    first_byte = b[0]
    if first_byte <= 0x7F:  # positive fixint
        obj = first_byte
    elif first_byte >= 0xE0:  # negative fixint
        obj = first_byte - 0x100
    elif first_byte <= 0x8F:  # fixmap
        ml = first_byte & 0x0F
        obj = {unpack_stream(stream): unpack_stream(stream) for _ in range(ml)}
    elif first_byte <= 0x9F:  # fixarray
        al = first_byte & 0x0F
        obj = [unpack_stream(stream) for _ in range(al)]
    elif first_byte <= 0xBF:  # fixstr
        sl = first_byte & 0x1F
        obj = stream.read(sl).decode("utf-8")
    elif first_byte == 0xC0:  # nil
        obj = None
    elif first_byte == 0xC1:  # (never used)
        raise ValueError("invalid first byte", first_byte, hex(first_byte))
    elif first_byte == 0xC2:  # false
        obj = False
    elif first_byte == 0xC3:  # true
        obj = True
    elif first_byte == 0xC4:  # bin8
        bl = u8_b_unpack(stream)
        obj = stream.read(bl)
    elif first_byte == 0xC5:  # bin16
        bl = u16_b_unpack(stream)
        obj = stream.read(bl)
    elif first_byte == 0xC6:  # bin32
        bl = u32_b_unpack(stream)
        obj = stream.read(bl)
    elif first_byte <= 0xC9:  # ext (0xC7 - 0xC9)
        if first_byte == 0xC7:
            extl = u8_b_unpack(stream)  # ext8
        elif first_byte == 0xC8:
            extl = u16_b_unpack(stream)  # ext16
        else:
            extl = u32_b_unpack(stream)  # ext32
        code = s8_b_unpack(stream)
        data = stream.read(extl)
        if code < 0:  # reserved for msgpack
            if code == -1:  # timestamp
                # timestamp96
                if extl == 12:
                    (nanoseconds,) = u32_b_st.unpack(data[: u32_b_st.size])
                    (seconds,) = s64_b_st.unpack(data[u32_b_st.size :])
                else:
                    raise ValueError("invalid timestamp length", extl)
                obj = _timestamp_to_datetime(seconds, nanoseconds)
            else:
                raise NotImplementedError("unsupported reserved extension", code)
        else:
            obj = ExtType(code, data)
    elif first_byte == 0xCA:  # float32
        obj = f32_b_unpack(stream)
    elif first_byte == 0xCB:  # float64
        obj = f64_b_unpack(stream)
    elif first_byte == 0xCC:  # uint8
        obj = u8_b_unpack(stream)
    elif first_byte == 0xCD:  # uint16
        obj = u16_b_unpack(stream)
    elif first_byte == 0xCE:  # uint32
        obj = u32_b_unpack(stream)
    elif first_byte == 0xCF:  # uint64
        obj = u64_b_unpack(stream)
    elif first_byte == 0xD0:  # int8
        obj = s8_b_unpack(stream)
    elif first_byte == 0xD1:  # int16
        obj = s16_b_unpack(stream)
    elif first_byte == 0xD2:  # int32
        obj = s32_b_unpack(stream)
    elif first_byte == 0xD3:  # int64
        obj = s64_b_unpack(stream)
    elif first_byte <= 0xD8:  # fixext (0xD4 - 0xD8)
        code = s8_b_unpack(stream)
        extl = 1 << (first_byte - 0xD4)
        data = stream.read(extl)
        if code < 0:  # reserved for msgpack
            if code == -1:  # timestamp
                if extl == 4:
                    # timestamp32
                    (seconds,) = u32_b_st.unpack(data)
                    nanoseconds = 0
                elif extl == 8:
                    # timestamp64
                    (data64,) = u64_b_st.unpack(data)
                    nanoseconds = data64 >> _NS_MASK_LEN
                    seconds = data64 & _NS_MASK
                else:
                    raise ValueError("invalid timestamp length", extl)

                obj = _timestamp_to_datetime(seconds, nanoseconds)
            else:
                raise NotImplementedError("unsupported reserved extension", code)
        else:
            obj = ExtType(code, data)
    elif first_byte == 0xD9:  # str8
        sl = u8_b_unpack(stream)
        obj = stream.read(sl).decode("utf-8")
    elif first_byte == 0xDA:  # str16
        sl = u16_b_unpack(stream)
        obj = stream.read(sl).decode("utf-8")
    elif first_byte == 0xDB:  # str32
        sl = u32_b_unpack(stream)
        obj = stream.read(sl).decode("utf-8")
    elif first_byte <= 0xDD:  # array
        if first_byte == 0xDC:
            al = u16_b_unpack(stream)  # array16
        else:
            al = u32_b_unpack(stream)  # array32
        obj = [unpack_stream(stream) for _ in range(al)]
    elif first_byte <= 0xDF:  # map
        if first_byte == 0xDE:
            ml = u16_b_unpack(stream)  # map16
        else:
            ml = u32_b_unpack(stream)  # map32
        obj = {unpack_stream(stream): unpack_stream(stream) for _ in range(ml)}
    else:
        raise ValueError("invalid first byte", first_byte, hex(first_byte))
    return obj
