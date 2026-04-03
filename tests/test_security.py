import sys
from contextlib import contextmanager

import pytest

from msgpack_streams import pack, unpack


def get_stack_depth() -> int:
    """Return the current call stack depth."""
    depth = 0
    frame = sys._getframe()
    while frame:
        depth += 1
        frame = frame.f_back
    return depth


@contextmanager
def recursion_limit(limit: int):
    """Temporarily override Python's recursion limit."""
    previous_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(limit)
    try:
        yield
    finally:
        sys.setrecursionlimit(previous_limit)


def _nested_list(depth: int):
    obj = 0
    for _ in range(depth):
        obj = [obj]
    return obj


def test_get_stack_depth_increases_for_nested_calls():
    outer_depth = get_stack_depth()

    def nested() -> int:
        return get_stack_depth()

    nested_depth = nested()

    assert nested_depth == outer_depth + 1


def test_recursion_limit_context_manager_restores_previous_value():
    previous_limit = sys.getrecursionlimit()
    target_limit = previous_limit + 25

    with recursion_limit(target_limit):
        assert sys.getrecursionlimit() == target_limit

    assert sys.getrecursionlimit() == previous_limit


def test_pack_rejects_nested_payload_over_max_depth():
    with pytest.raises(RecursionError, match="max depth exceeded"):
        pack(_nested_list(3), max_depth=2)


def test_unpack_rejects_nested_payload_over_max_depth():
    data = pack(_nested_list(3))

    with pytest.raises(RecursionError, match="max depth exceeded"):
        unpack(data, max_depth=2)


def test_scalar_root_is_allowed_at_low_depth():
    assert pack(1, max_depth=1) == b"\x01"
    assert unpack(b"\x01", max_depth=1) == (1, b"")


def test_container_root_is_not_allowed_at_low_depth():
    with pytest.raises(RecursionError, match="max depth exceeded"):
        pack(_nested_list(1), max_depth=1)


def test_recursion_limit_pack():
    limit = sys.getrecursionlimit() - get_stack_depth()
    obj = _nested_list(limit)

    assert obj
    pack(obj[0])

    with pytest.raises(RecursionError, match="maximum recursion depth exceeded"):
        pack(obj)


def test_recursion_limit_unpack():
    previous_limit = sys.getrecursionlimit()
    with recursion_limit(previous_limit + get_stack_depth() + 1):
        data = pack(_nested_list(previous_limit))
    with pytest.raises(RecursionError, match="maximum recursion depth exceeded"):
        unpack(data)
