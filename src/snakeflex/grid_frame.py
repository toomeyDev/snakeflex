"""snakeflex.grid_frame — CSS Grid-inspired layout container.

Implements a subset of CSS Grid using tkinter's grid() geometry manager.

Template syntax
---------------
Column and row sizes are specified as space-separated track definitions::

    "200px 1fr 2fr"      → fixed 200 px | 1 part | 2 parts of remaining space
    "1fr 1fr 1fr"        → three equal columns
    "auto 1fr"           → one content-sized column, one that fills the rest
    "48px 1fr 28px"      → fixed header, flexible content, fixed footer

Supported track tokens
----------------------
    Npx   → fixed size in pixels      (columnconfigure minsize=N, weight=0)
    Nfr   → fractional unit           (columnconfigure weight=N)
    auto  → size to content           (columnconfigure weight=0, minsize=0)

Usage
-----
::

    from snakeflex import GridFrame

    layout = GridFrame(parent, columns="220px 1fr", rows="48px 1fr 28px", gap=0)
    layout.add(topbar,   col=0, row=0, colspan=2)
    layout.add(sidebar,  col=0, row=1)
    layout.add(content,  col=1, row=1)
    layout.add(statusbar,col=0, row=2, colspan=2)

Responsive breakpoints (via ResponsiveMixin)
--------------------------------------------
::

    layout.on_resize(800,
        narrow=lambda: layout.hide_col(2),
        wide=lambda:   layout.show_col(2),
    )
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from ._base import _FlexBase


# ── Track parser ──────────────────────────────────────────────────────────────

@dataclass
class _Track:
    kind:    str    # "px" | "fr" | "auto"
    value:   float  # pixel count for "px", weight for "fr", 0 for "auto"
    hidden:  bool = False


def _parse_template(template: str) -> List[_Track]:
    """Parse a template string into a list of _Track objects."""
    tracks: List[_Track] = []
    for token in template.strip().split():
        token = token.strip().lower()
        if token.endswith("fr"):
            tracks.append(_Track("fr", float(token[:-2])))
        elif token.endswith("px"):
            tracks.append(_Track("px", float(token[:-2])))
        elif token == "auto":
            tracks.append(_Track("auto", 0))
        else:
            raise ValueError(
                f"snakeflex: unknown track token {token!r}. "
                "Expected 'Npx', 'Nfr', or 'auto'."
            )
    return tracks


# ── Child placement info ──────────────────────────────────────────────────────

@dataclass
class _CellInfo:
    widget:  tk.Widget
    col:     int
    row:     int
    colspan: int = 1
    rowspan: int = 1
    sticky:  str = "nsew"


# ── GridFrame ─────────────────────────────────────────────────────────────────

class GridFrame(_FlexBase):
    """A frame whose children are placed in a CSS Grid-like layout.

    Parameters
    ----------
    parent:
        Parent widget.
    columns:
        Space-separated column track definitions (``"px"``, ``"fr"``, ``"auto"``).
    rows:
        Space-separated row track definitions.
    gap:
        Pixels of uniform gap between all cells.  Applied as ``padx``/``pady``
        on each child.
    fg_color:
        Background colour or ``"transparent"`` (customtkinter-compatible).
    """

    def __init__(
        self,
        parent: tk.Widget,
        *,
        columns: str = "1fr",
        rows:    str = "1fr",
        gap:     int = 0,
        fg_color: str = "transparent",
        **kw,
    ) -> None:
        super().__init__(parent, fg_color=fg_color, **kw)
        self._col_tracks: List[_Track] = _parse_template(columns)
        self._row_tracks: List[_Track] = _parse_template(rows)
        self._gap  = max(0, int(gap))
        self._cells: List[_CellInfo] = []

        # Responsive breakpoint state
        self._breakpoints: Dict[int, Tuple[Optional[Callable], Optional[Callable]]] = {}
        self._last_width: Optional[int] = None
        self.bind("<Configure>", self._on_configure)

        self._apply_tracks()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        widget: tk.Widget,
        *,
        col:     int = 0,
        row:     int = 0,
        colspan: int = 1,
        rowspan: int = 1,
        sticky:  str = "nsew",
    ) -> tk.Widget:
        """Place *widget* in the grid at (*col*, *row*).

        Parameters
        ----------
        widget:
            Any tkinter or customtkinter widget.
        col, row:
            Zero-based grid position.
        colspan, rowspan:
            Number of tracks to span.
        sticky:
            tkinter sticky string (default ``"nsew"`` fills the cell).

        Returns
        -------
        widget
            The same widget, for chaining.
        """
        self._cells.append(_CellInfo(widget, col, row, colspan, rowspan, sticky))
        self._schedule_relayout()
        return widget

    # ------------------------------------------------------------------
    # Column / row visibility (for responsive use)
    # ------------------------------------------------------------------

    def hide_col(self, index: int) -> None:
        """Collapse column *index* to zero width."""
        if 0 <= index < len(self._col_tracks):
            self._col_tracks[index].hidden = True
            self._apply_tracks()
            self._relayout_cells()

    def show_col(self, index: int) -> None:
        """Restore column *index* to its defined size."""
        if 0 <= index < len(self._col_tracks):
            self._col_tracks[index].hidden = False
            self._apply_tracks()
            self._relayout_cells()

    def hide_row(self, index: int) -> None:
        """Collapse row *index* to zero height."""
        if 0 <= index < len(self._row_tracks):
            self._row_tracks[index].hidden = True
            self._apply_tracks()
            self._relayout_cells()

    def show_row(self, index: int) -> None:
        """Restore row *index* to its defined size."""
        if 0 <= index < len(self._row_tracks):
            self._row_tracks[index].hidden = False
            self._apply_tracks()
            self._relayout_cells()

    # ------------------------------------------------------------------
    # Responsive breakpoints
    # ------------------------------------------------------------------

    def on_resize(
        self,
        width: int,
        *,
        narrow: Optional[Callable] = None,
        wide:   Optional[Callable] = None,
    ) -> None:
        """Register callbacks for when the frame crosses *width* pixels.

        Parameters
        ----------
        width:
            Pixel threshold.
        narrow:
            Called when frame width drops *below* *width*.
        wide:
            Called when frame width is *at or above* *width*.
        """
        self._breakpoints[width] = (narrow, wide)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _apply_tracks(self) -> None:
        """Apply column/row weights and minsizes from track definitions."""
        for i, t in enumerate(self._col_tracks):
            if t.hidden:
                self.columnconfigure(i, weight=0, minsize=0)
            elif t.kind == "fr":
                self.columnconfigure(i, weight=int(t.value), minsize=0)
            elif t.kind == "px":
                self.columnconfigure(i, weight=0, minsize=int(t.value))
            else:  # auto
                self.columnconfigure(i, weight=0, minsize=0)

        for i, t in enumerate(self._row_tracks):
            if t.hidden:
                self.rowconfigure(i, weight=0, minsize=0)
            elif t.kind == "fr":
                self.rowconfigure(i, weight=int(t.value), minsize=0)
            elif t.kind == "px":
                self.rowconfigure(i, weight=0, minsize=int(t.value))
            else:  # auto
                self.rowconfigure(i, weight=0, minsize=0)

    def _relayout_cells(self) -> None:
        """Re-grid all registered children."""
        half = self._gap // 2
        for cell in self._cells:
            cell.widget.grid(
                row=cell.row,    column=cell.col,
                rowspan=cell.rowspan, columnspan=cell.colspan,
                sticky=cell.sticky,
                padx=half, pady=half,
            )

    def _do_relayout(self) -> None:
        self._relayout_pending = False
        self._apply_tracks()
        self._relayout_cells()

    # Debounce timer id for _on_configure
    _debounce_id: Optional[str] = None

    def _on_configure(self, event: tk.Event) -> None:
        """Debounced <Configure> handler for responsive breakpoints."""
        if self._debounce_id is not None:
            try:
                self.after_cancel(self._debounce_id)
            except Exception:
                pass
        self._debounce_id = self.after(50, self._check_breakpoints)

    def _check_breakpoints(self) -> None:
        self._debounce_id = None
        try:
            w = self.winfo_width()
        except tk.TclError:
            return
        if w == self._last_width:
            return
        prev = self._last_width
        self._last_width = w

        for threshold, (narrow_cb, wide_cb) in self._breakpoints.items():
            if prev is None:
                # First measurement — fire whichever applies
                if w < threshold and narrow_cb:
                    narrow_cb()
                elif w >= threshold and wide_cb:
                    wide_cb()
            else:
                crossed_to_narrow = prev >= threshold > w
                crossed_to_wide   = prev < threshold <= w
                if crossed_to_narrow and narrow_cb:
                    narrow_cb()
                elif crossed_to_wide and wide_cb:
                    wide_cb()
