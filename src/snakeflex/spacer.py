"""snakeflex.spacer — invisible, expanding spacer widget.

A Spacer is a transparent zero-size frame that consumes free space when
placed inside a FlexRow or FlexCol with grow=1 (the default).  It is the
tkinter equivalent of:

    <div style="flex: 1" />

or Bootstrap's ``ms-auto`` / ``me-auto`` utility classes.

Usage::

    row = FlexRow(parent, justify="start", gap=8)
    row.add(logo)
    row.add(Spacer())     # pushes everything to the right
    row.add(settings_btn)
    row.add(close_btn)
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional

from ._base import _FlexBase, _resolve_bg


class Spacer(_FlexBase):
    """A transparent, expanding spacer.

    Parameters
    ----------
    parent:
        Parent widget.
    fg_color:
        Passed through to the underlying tk.Frame.  Defaults to
        ``"transparent"`` so it blends into most backgrounds.
    """

    def __init__(self, parent: Optional[tk.Widget] = None, *,
                 fg_color: str = "transparent", **kw) -> None:
        self._deferred_parent = parent is None
        if parent is None:
            # Use a temporary placeholder; will be re-parented on add().
            parent = tk.Frame.__new__(tk.Frame)
        super().__init__(parent, fg_color=fg_color, **kw)

    def _do_relayout(self) -> None:
        self._relayout_pending = False
