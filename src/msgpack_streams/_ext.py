from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtType:
    """Extension type."""

    code: int
    """Type code (0-127)."""
    data: bytes
    """Raw data (up to 2^32-1 bytes)."""
