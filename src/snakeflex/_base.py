"""snakeflex._base — shared base class for all layout containers.

Provides:
  • fg_color kwarg → bg shim (customtkinter compatibility)
  • transparent background resolution by walking the parent widget tree
  • coalesced after(0) relayout scheduling
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional


def _resolve_bg(parent: tk.Widget, fg_color: Optional[str]) -> Optional[str]:
    """Map fg_color to a real tk bg colour string.

    Rules
    -----
    None          → don't set bg at all (inherit Tk default)
    "transparent" → walk up the parent tree until a concrete bg is found
    anything else → use as-is
    """
    if fg_color is None:
        return None
    if fg_color != "transparent":
        return fg_color
    # Walk up looking for a concrete colour.
    # Use the low-level Tk call (bypasses CTk's cget() Python override, which
    # raises ValueError for "bg" on CTkFrame / CTkBaseClass widgets).
    node = parent
    while node is not None:
        try:
            bg = str(node.tk.call(str(node), "cget", "-background"))
            if bg and bg != "transparent":
                return bg
        except Exception:
            pass
        node = getattr(node, "master", None)
    return None      # give up; Tk will use its default


class _FlexBase(tk.Frame):
    """Base frame for FlexFrame and GridFrame.

    Accepts ``fg_color`` as an alias for ``bg`` so code written against
    customtkinter's CTkFrame API compiles without modification::

        FlexRow(parent, fg_color="#1e1e2e")
        FlexRow(parent, fg_color="transparent")
        FlexRow(parent, bg="#1e1e2e")          # plain tk style also works
    """

    def __init__(self, parent: tk.Widget, *, fg_color: Optional[str] = "transparent",
                 **kw) -> None:
        # Resolve fg_color → bg before tk.Frame() runs so the frame is
        # created with the right colour from the start.
        if fg_color is not None and "bg" not in kw:
            resolved = _resolve_bg(parent, fg_color)
            if resolved is not None:
                kw["bg"] = resolved

        super().__init__(parent, **kw)
        self._relayout_pending = False

    def _schedule_relayout(self) -> None:
        """Queue a relayout on the next idle tick, coalescing multiple calls."""
        if not self._relayout_pending:
            self._relayout_pending = True
            self.after(0, self._do_relayout)

    def _do_relayout(self) -> None:
        """Subclasses override this to perform the actual grid reconfiguration."""
        self._relayout_pending = False
