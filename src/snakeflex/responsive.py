"""snakeflex.responsive — ResponsiveMixin for any tk widget.

Allows any tk.Frame subclass (or GridFrame/FlexFrame) to register callbacks
that fire when the widget width crosses defined pixel thresholds.

Usage
-----
::

    class MyPanel(ResponsiveMixin, tk.Frame):
        def __init__(self, parent):
            tk.Frame.__init__(self, parent)
            ResponsiveMixin.__init__(self)
            self.on_resize(700,
                narrow=self._compact_layout,
                wide=self._full_layout,
            )

    # Or use directly on an existing GridFrame / FlexFrame —
    # those classes already embed this logic via GridFrame.on_resize().
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, Optional, Tuple


class ResponsiveMixin:
    """Mixin that adds width-breakpoint callbacks to any tk widget.

    The host class must be a tk widget (has ``winfo_width``, ``bind``,
    ``after``, ``after_cancel``).

    Call ``ResponsiveMixin.__init__(self)`` in the host's ``__init__``
    *after* the tk.Frame constructor has run.
    """

    def __init__(self) -> None:
        self._rm_breakpoints: Dict[int, Tuple[Optional[Callable], Optional[Callable]]] = {}
        self._rm_last_width: Optional[int] = None
        self._rm_debounce_id: Optional[str] = None
        # Bind on the widget itself (self must be a tk widget)
        self.bind("<Configure>", self._rm_on_configure, add="+")  # type: ignore[attr-defined]

    def on_resize(
        self,
        width: int,
        *,
        narrow: Optional[Callable] = None,
        wide:   Optional[Callable] = None,
    ) -> None:
        """Register callbacks for when the widget crosses *width* pixels wide.

        Parameters
        ----------
        width:
            The pixel threshold.
        narrow:
            Called once when width drops *below* the threshold.
        wide:
            Called once when width reaches or exceeds the threshold.
        """
        self._rm_breakpoints[width] = (narrow, wide)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rm_on_configure(self, event: tk.Event) -> None:
        if self._rm_debounce_id is not None:
            try:
                self.after_cancel(self._rm_debounce_id)  # type: ignore[attr-defined]
            except Exception:
                pass
        self._rm_debounce_id = self.after(50, self._rm_check)  # type: ignore[attr-defined]

    def _rm_check(self) -> None:
        self._rm_debounce_id = None
        try:
            w = self.winfo_width()  # type: ignore[attr-defined]
        except tk.TclError:
            return

        prev = self._rm_last_width
        if w == prev:
            return
        self._rm_last_width = w

        for threshold, (narrow_cb, wide_cb) in self._rm_breakpoints.items():
            if prev is None:
                if w < threshold and narrow_cb:
                    narrow_cb()
                elif w >= threshold and wide_cb:
                    wide_cb()
            else:
                if prev >= threshold > w and narrow_cb:
                    narrow_cb()
                elif prev < threshold <= w and wide_cb:
                    wide_cb()
