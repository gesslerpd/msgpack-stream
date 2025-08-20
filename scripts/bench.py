import os

# set before importing `msgpack`
os.environ["MSGPACK_PUREPYTHON"] = "1"

from msgpack_stream import unpack, unpack_stream, pack, pack_stream
from mmap import mmap, ACCESS_READ, ACCESS_WRITE
import argparse
import timeit

from msgpack import unpackb, packb


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, default=25, help="Number of runs")
    parser.add_argument(
        "-m", "--mapped", action="store_true", help="Use memory mapping"
    )
    args = parser.parse_args()

    _globals = {
        "main": main,
        "stream": stream,
        "other": other,
        "mapped": args.mapped,
    }

    _serialize = {
        "main": serialize_main,
        "stream": serialize_stream,
        "other": serialize_other,
        "obj": stream(False),
        "mapped": args.mapped,
    }

    t_main = timeit.timeit("main(mapped)", number=args.number, globals=_globals)
    t_stream = timeit.timeit("stream(mapped)", number=args.number, globals=_globals)
    t_other = timeit.timeit("other(mapped)", number=args.number, globals=_globals)

    print(f"main: {t_main:.6f}s total, {t_main / args.number:.6f}s per call")
    print(f"stream: {t_stream:.6f}s total, {t_stream / args.number:.6f}s per call")
    print(f"other: {t_other:.6f}s total, {t_other / args.number:.6f}s per call")

    t_main_s = timeit.timeit(
        "main(obj, mapped)", number=args.number, globals=_serialize
    )
    t_stream_s = timeit.timeit(
        "stream(obj, mapped)", number=args.number, globals=_serialize
    )
    t_other_s = timeit.timeit(
        "other(obj, mapped)", number=args.number, globals=_serialize
    )

    print(
        f"main serialize: {t_main_s:.6f}s total, {t_main_s / args.number:.6f}s per call"
    )
    print(
        f"stream serialize: {t_stream_s:.6f}s total, {t_stream_s / args.number:.6f}s per call"
    )
    print(
        f"other serialize: {t_other_s:.6f}s total, {t_other_s / args.number:.6f}s per call"
    )
