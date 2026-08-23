"""Planemo's shared :mod:`rich` console.

Rich installs at most one live display per console, and redirects ``stdout``
and ``stderr`` through that console while a display is running. Handing every
display the same console keeps those two facts true of Planemo as a whole
rather than of one display at a time.
"""

from typing import Optional

from rich.console import Console

_console: Optional[Console] = None


def planemo_console() -> Console:
    """Return the console Planemo renders all of its live displays through."""
    global _console
    if _console is None:
        _console = Console()
    return _console


__all__ = ("planemo_console",)
