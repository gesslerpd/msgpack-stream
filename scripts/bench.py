import gc
import os

# set before importing `msgpack`
os.environ["MSGPACK_PUREPYTHON"] = "1"

import argparse
import timeit
from mmap import ACCESS_READ, ACCESS_WRITE, mmap

from msgpack import packb, unpackb

from msgpack_streams import pack, pack_stream, unpack, unpack_stream

FILE = "scripts/obj.msgpack"


def main(mapped):
    with open(FILE, "rb") as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpack(mm.read())
        else:
            return unpack(fd.read())


def stream(mapped):
    with open(FILE, "rb") as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpack_stream(mm)
        else:
            return unpack_stream(fd)


def other(mapped):
    with open(FILE, "rb") as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpackb(mm.read(), strict_map_key=False)
        else:
            return unpackb(fd.read(), strict_map_key=False)


def serialize_main(obj, mapped):
    with open("temp", "wb") as fd:
        if mapped:
            with mmap(-1, 3955122, access=ACCESS_WRITE) as mm:
                mm.write(pack(obj))
        else:
            fd.write(pack(obj))


def serialize_stream(obj, mapped):
    with open("temp", "wb") as fd:
        if mapped:
            with mmap(-1, 3955122, access=ACCESS_WRITE) as mm:
                pack_stream(mm, obj)
        else:
            pack_stream(fd, obj)


def serialize_other(obj, mapped):
    with open("temp", "wb") as fd:
        if mapped:
            with mmap(-1, 3955122, access=ACCESS_WRITE) as mm:
                mm.write(packb(obj))
        else:
            fd.write(packb(obj))


RAW_OBJ = stream(False)
RAW_DATA = pack(RAW_OBJ)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, default=25, help="Number of runs")
    parser.add_argument("-m", "--mapped", action="store_true", help="Use memory mapping")
    args = parser.parse_args()

    _globals = {
        "main": main,
        "stream": stream,
        "raw": unpack,
        "other": other,
        "other_raw": unpackb,
        "data": RAW_DATA,
        "mapped": args.mapped,
    }

    _serialize = {
        "main": serialize_main,
        "stream": serialize_stream,
        "raw": pack,
        "other": serialize_other,
        "other_raw": packb,
        "obj": RAW_OBJ,
        "mapped": args.mapped,
    }

    gc.disable()

    t_main = timeit.timeit("main(mapped)", number=args.number, globals=_globals)
    t_stream = timeit.timeit("stream(mapped)", number=args.number, globals=_globals)
    t_raw = timeit.timeit("raw(data)", number=args.number, globals=_globals)
    t_other = timeit.timeit("other(mapped)", number=args.number, globals=_globals)
    t_other_raw = timeit.timeit(
        "other_raw(data, strict_map_key=False)", number=args.number, globals=_globals
    )

    gc.enable()
    gc.collect()

    print(
        f"main: {t_main:.6f}s total, {t_main / args.number:.6f}s per call ({t_other / t_main:.2f}x speedup vs msgpack)"
    )
    print(
        f"stream: {t_stream:.6f}s total, {t_stream / args.number:.6f}s per call ({t_other / t_stream:.2f}x speedup vs msgpack)"
    )
    print(
        f"raw (unpack bytes): {t_raw:.6f}s total, {t_raw / args.number:.6f}s per call ({t_other_raw / t_raw:.2f}x speedup vs msgpack raw)"
    )
    print(f"other (msgpack): {t_other:.6f}s total, {t_other / args.number:.6f}s per call")
    print(
        f"other_raw (unpackb bytes): {t_other_raw:.6f}s total, {t_other_raw / args.number:.6f}s per call"
    )

    gc.disable()

    t_main_s = timeit.timeit("main(obj, mapped)", number=args.number, globals=_serialize)
    t_stream_s = timeit.timeit("stream(obj, mapped)", number=args.number, globals=_serialize)
    t_raw_s = timeit.timeit("raw(obj)", number=args.number, globals=_serialize)
    t_other_s = timeit.timeit("other(obj, mapped)", number=args.number, globals=_serialize)
    t_other_raw_s = timeit.timeit("other_raw(obj)", number=args.number, globals=_serialize)

    gc.enable()
    gc.collect()

    print(
        f"main serialize: {t_main_s:.6f}s total, {t_main_s / args.number:.6f}s per call ({t_other_s / t_main_s:.2f}x speedup vs msgpack)"
    )
    print(
        f"stream serialize: {t_stream_s:.6f}s total, {t_stream_s / args.number:.6f}s per call ({t_other_s / t_stream_s:.2f}x speedup vs msgpack)"
    )
    print(
        f"raw serialize (pack bytes): {t_raw_s:.6f}s total, {t_raw_s / args.number:.6f}s per call ({t_other_raw_s / t_raw_s:.2f}x speedup vs msgpack raw)"
    )
    print(
        f"other serialize (msgpack): {t_other_s:.6f}s total, {t_other_s / args.number:.6f}s per call"
    )
    print(
        f"other_raw serialize (packb bytes): {t_other_raw_s:.6f}s total, {t_other_raw_s / args.number:.6f}s per call"
    )
