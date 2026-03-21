"""snakeflex.flex — FlexFrame, FlexRow, FlexCol.

Implements CSS Flexbox semantics over tkinter's grid() geometry manager.

Layout model
------------
All children are placed in a single row (direction="row") or column
(direction="column") of a grid.  flex-grow maps directly to grid weight.
justify-content is implemented via phantom weight-1 columns/rows inserted
at the right positions — no actual spacer widgets are needed (except when
the caller explicitly uses Spacer()).  gap is applied as asymmetric padx/pady
on each child so no extra frames are inserted between items.

Supported justify values
------------------------
    "start"        (default) items packed to the start; free space trails
    "end"          items packed to the end; free space leads
    "center"       items centered; free space split evenly on both sides
    "space-between" free space distributed between items
    "space-around"  free space distributed around each item (half-gap at edges)
    "space-evenly"  equal free space between every pair including edges

Supported align values
----------------------
    "stretch"  (default) children fill the cross-axis
    "start"    children aligned to the start of the cross-axis
    "end"      children aligned to the end of the cross-axis
    "center"   children centered on the cross-axis
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from ._base import _FlexBase
from .spacer import Spacer

Direction = Literal["row", "column", "row-reverse", "column-reverse"]
Justify   = Literal["start", "end", "center", "space-between", "space-around", "space-evenly"]
Align     = Literal["stretch", "start", "end", "center"]


@dataclass
class _ChildInfo:
    widget: tk.Widget
    grow:   int                  # flex-grow (0 = size to content)
    align:  Optional[Align]      # align-self override (None = inherit container align)


class FlexFrame(_FlexBase):
    """A frame that arranges children using CSS Flexbox-inspired rules.

    Parameters
    ----------
    parent:
        Parent widget.
    direction:
        ``"row"`` (default) lays children out left-to-right.
        ``"column"`` lays them top-to-bottom.
        ``"row-reverse"`` and ``"column-reverse"`` reverse the order.
    justify:
        How to distribute free space along the main axis.
        One of ``"start"``, ``"end"``, ``"center"``, ``"space-between"``,
        ``"space-around"``, ``"space-evenly"``.
    align:
        How to align children along the cross axis.
        One of ``"stretch"``, ``"start"``, ``"end"``, ``"center"``.
    gap:
        Pixels of space between children (like CSS ``gap``).
    fg_color:
        Background colour or ``"transparent"`` (customtkinter-compatible).
    """

    def __init__(
        self,
        parent: tk.Widget,
        *,
        direction: Direction = "row",
        justify:   Justify   = "start",
        align:     Align     = "stretch",
        gap:       int       = 0,
        fg_color:  str       = "transparent",
        **kw,
    ) -> None:
        super().__init__(parent, fg_color=fg_color, **kw)
        self._direction = direction
        self._justify   = justify
        self._align     = align
        self._gap       = max(0, int(gap))
        self._children: List[_ChildInfo] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, widget: tk.Widget, *, grow: int = 0,
            align: Optional[Align] = None) -> tk.Widget:
        """Add *widget* as the next child in the flex container.

        Parameters
        ----------
        widget:
            Any tkinter or customtkinter widget.  Must have *self* as its
            parent (or an ancestor).
        grow:
            How much spare space this child claims relative to its siblings.
            ``0`` = size to content (default).
            ``1`` or more = proportional share of remaining space.
        align:
            Per-child override for the container's ``align`` setting.

        Returns
        -------
        widget
            The same widget passed in, so calls can be chained::

                row.add(ctk.CTkButton(row, text="OK"), grow=1)
        """
        if isinstance(widget, Spacer):
            grow = grow or 1        # Spacer defaults to grow=1
        self._children.append(_ChildInfo(widget=widget, grow=grow, align=align))
        self._schedule_relayout()
        return widget

    # ------------------------------------------------------------------
    # Layout engine
    # ------------------------------------------------------------------

    @property
    def _is_row(self) -> bool:
        return self._direction in ("row", "row-reverse")

    @property
    def _is_reversed(self) -> bool:
        return self._direction in ("row-reverse", "column-reverse")

    def _do_relayout(self) -> None:
        self._relayout_pending = False
        if not self._children:
            return

        items = list(reversed(self._children)) if self._is_reversed else list(self._children)
        has_grow = any(c.grow > 0 for c in items)
        n = len(items)

        # Reset all existing grid config 
        _max = n * 3 + 4
        if self._is_row:
            for i in range(_max):
                self.columnconfigure(i, weight=0, minsize=0, pad=0)
            self.rowconfigure(0, weight=0)
        else:
            for i in range(_max):
                self.rowconfigure(i, weight=0, minsize=0, pad=0)
            self.columnconfigure(0, weight=0)

        # Clear previous grid placements
        for info in self._children:
            try:
                info.widget.grid_forget()
            except tk.TclError:
                pass

        #  compute slot indices (main axis) 
        # Slots interleave items with phantom spacer columns (no widget,
        # just grid weight) for justify-content and gap columns.
        slots: List[Optional[_ChildInfo]] = []   # None = phantom spacer slot

        if self._justify == "end" and not has_grow:
            slots.append(None) # leading spacer
        elif self._justify == "center" and not has_grow:
            slots.append(None) # leading spacer
        elif self._justify in ("space-around", "space-evenly") and not has_grow:
            slots.append(None) # leading spacer

        for i, info in enumerate(items):
            slots.append(info)
            if i < n - 1:
                # Between-item slot: gap OR space-between/around phantom
                if not has_grow and self._justify in (
                    "space-between", "space-around", "space-evenly"
                ):
                    slots.append(None) # phantom spacer between items
                elif self._gap > 0:
                    slots.append(None) # gap placeholder (minsize, weight=0)

        if not has_grow and self._justify in (
            "start", "center", "space-around", "space-evenly"
        ):
            slots.append(None)                   # trailing spacer

        # apply grid configuration 
        cross_weight = 1 if self._align == "stretch" else 0

        if self._is_row:
            self.rowconfigure(0, weight=cross_weight)
        else:
            self.columnconfigure(0, weight=cross_weight)

        item_idx = 0 # counts actual children placed (for gap padding)
        for slot_idx, slot in enumerate(slots):
            if self._is_row:
                main_axis_cfg = lambda idx, **kw: self.columnconfigure(idx, **kw)
                def place(w, idx, sticky):
                    half_before, half_after = self._gap_padding(item_idx, n)
                    w.grid(row=0, column=idx, sticky=sticky,
                           padx=(half_before, half_after), pady=0)
            else:
                main_axis_cfg = lambda idx, **kw: self.rowconfigure(idx, **kw)
                def place(w, idx, sticky):
                    half_before, half_after = self._gap_padding(item_idx, n)
                    w.grid(row=idx, column=0, sticky=sticky,
                           padx=0, pady=(half_before, half_after))

            if slot is None:
                # Phantom spacer slot
                is_gap_slot = (
                    self._gap > 0
                    and not has_grow
                    and self._justify == "start"
                    and slot_idx > 0
                    and slot_idx < len(slots) - 1
                )
                if is_gap_slot:
                    # Fixed-size gap column, no weight
                    main_axis_cfg(slot_idx, weight=0, minsize=self._gap)
                else:
                    # Stretchy spacer for justify-content
                    main_axis_cfg(slot_idx, weight=1, minsize=0)
            else:
                # Real child
                main_axis_cfg(slot_idx, weight=slot.grow)
                sticky = self._sticky(slot.align)
                place(slot.widget, slot_idx, sticky)
                item_idx += 1

    def _gap_padding(self, item_idx: int, n: int):
        """Return (pad_before, pad_after) for the item at position item_idx."""
        if self._gap == 0 or self._justify not in ("start", "end", "center"):
            return 0, 0
        half = self._gap // 2
        if n == 1:
            return 0, 0
        if item_idx == 0:
            return 0, half
        if item_idx == n - 1:
            return half, 0
        return half, half

    def _sticky(self, item_align: Optional[Align]) -> str:
        """Convert align to a tk grid sticky string."""
        effective = item_align or self._align
        if self._is_row:
            # Cross axis = vertical
            return {"stretch": "ns", "start": "n", "end": "s", "center": ""}[effective]
        else:
            # Cross axis = horizontal
            return {"stretch": "ew", "start": "w", "end": "e", "center": ""}[effective]


# ------------------------------------------------------------------
# Convenience subclasses (thin wrappers)
# ------------------------------------------------------------------

class FlexRow(FlexFrame):
    """Horizontal flex container. Equivalent to ``FlexFrame(direction="row")``.

    Example::

        bar = FlexRow(parent, justify="space-between", align="center", gap=8)
        bar.add(logo)
        bar.add(Spacer())
        bar.add(menu_btn)
    """

    def __init__(self, parent: tk.Widget, **kw) -> None:
        kw.setdefault("direction", "row")
        super().__init__(parent, **kw)


class FlexCol(FlexFrame):
    """Vertical flex container. Equivalent to ``FlexFrame(direction="column")``.

    Example::

        panel = FlexCol(parent, align="stretch", gap=4)
        panel.add(header)
        panel.add(content, grow=1)
        panel.add(footer)
    """

    def __init__(self, parent: tk.Widget, **kw) -> None:
        kw.setdefault("direction", "column")
        super().__init__(parent, **kw)
