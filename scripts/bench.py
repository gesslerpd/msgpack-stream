import os

# set before importing `msgpack`
os.environ["MSGPACK_PUREPYTHON"] = "1"

from msgpack_stream import unpack, unpack_stream
from mmap import mmap, ACCESS_READ
import argparse
import timeit

from msgpack import unpackb


FILE = "scripts/obj.msgpack"


def main(mapped):
    with open(FILE, "rb", buffering=0) as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpack(mm.read())
        else:
            return unpack(fd.read())


def stream(mapped):
    with open(FILE, "rb", buffering=0) as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpack_stream(mm)
        else:
            return unpack_stream(fd)


def other(mapped):
    with open(FILE, "rb", buffering=0) as fd:
        if mapped:
            with mmap(fd.fileno(), 0, access=ACCESS_READ) as mm:
                return unpackb(mm.read(), strict_map_key=False)
        else:
            return unpackb(fd.read(), strict_map_key=False)


if __name__ == "__main__":
    _globals = {
        "main": main,
        "stream": stream,
        "other": other,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, default=25, help="Number of runs")
    args = parser.parse_args()

    t_main = timeit.timeit("main(True)", number=args.number, globals=_globals)
    # this needs to be mmap for good performance
    t_stream = timeit.timeit("stream(True)", number=args.number, globals=_globals)
    t_other = timeit.timeit("other(True)", number=args.number, globals=_globals)

    print(f"main: {t_main:.6f}s total, {t_main / args.number:.6f}s per call")
    print(f"stream: {t_stream:.6f}s total, {t_stream / args.number:.6f}s per call")
    print(f"other: {t_other:.6f}s total, {t_other / args.number:.6f}s per call")
