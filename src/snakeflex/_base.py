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
    """Map fg_color to a valid tk color string.

    Rules
    -----
    - None:          use TK default, don't set bg at all
    - "transparent": get the bg from the parent tree
    - other: use as-is
    """
    if fg_color is None:
        return None
    if fg_color != "transparent":
        return fg_color
    # Traverse to find a TK color for the element.
    # raises ValueError for "bg" on CTkFrame / CTkBaseClass widgets),
    # so use base tk instead of ctk for this.
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
    customtkinter's CTkFrame API is compatible::

        FlexRow(parent, fg_color="#1e1e2e")
        FlexRow(parent, fg_color="transparent")
        FlexRow(parent, bg="#1e1e2e")          # plain tk style also works
    """

    def __init__(self, parent: tk.Widget, *, fg_color: Optional[str] = "transparent",
                 **kw) -> None:
        self._fg_color = fg_color

        # Resolve fg_color → bg before tk.Frame() runs so the frame is
        # created with the right colour from the start.
        if fg_color is not None and "bg" not in kw:
            resolved = _resolve_bg(parent, fg_color)
            if resolved is not None:
                kw["bg"] = resolved

        super().__init__(parent, **kw)
        self._relayout_pending = False

    def update_bg(self, bg: Optional[str] = None) -> None:
        """Re-resolve or set the background colour.

        If *bg* is provided, apply it directly.  If *bg* is ``None`` and this
        widget was created with ``fg_color="transparent"``, hit the parent to
        grab the color.
        .
        """
        if bg is not None:
            self.configure(bg=bg)
            return
        if self._fg_color == "transparent":
            resolved = _resolve_bg(self.master, "transparent")
            if resolved is not None:
                self.configure(bg=resolved)

    @staticmethod
    def update_tree(widget: tk.Widget) -> None:
        """Recursively call :meth:`update_bg` on every ``_FlexBase`` in the tree."""
        for child in widget.winfo_children():
            if isinstance(child, _FlexBase):
                try:
                    child.update_bg()
                except Exception:
                    pass
            _FlexBase.update_tree(child)

    def _schedule_relayout(self) -> None:
        """Queue a relayout on the next idle tick, coalescing multiple calls."""
        if not self._relayout_pending:
            self._relayout_pending = True
            self.after(0, self._do_relayout)

    def _do_relayout(self) -> None:
        """Subclasses override this to perform the actual grid reconfiguration."""
        self._relayout_pending = False
