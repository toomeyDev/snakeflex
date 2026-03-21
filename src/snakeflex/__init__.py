"""snakeflex — Flexbox and CSS Grid-inspired layout primitives for tkinter.

Works with standard tkinter and customtkinter widgets.  Zero external
dependencies — just Python and tkinter.

Quick start
-----------
::

    from snakeflex import FlexRow, FlexCol, GridFrame, Spacer

    # Horizontal bar: left label, growing spacer, right button
    bar = FlexRow(parent, justify="space-between", align="center", gap=8)
    bar.add(title_label)
    bar.add(Spacer())
    bar.add(settings_btn)

    # Vertical panel: fixed header, growing content, fixed footer
    panel = FlexCol(parent, align="stretch", gap=4)
    panel.add(header, grow=0)
    panel.add(content, grow=1)
    panel.add(footer, grow=0)

    # CSS Grid with fr units
    layout = GridFrame(parent, columns="220px 1fr", rows="48px 1fr 28px")
    layout.add(topbar,    col=0, row=0, colspan=2)
    layout.add(sidebar,   col=0, row=1)
    layout.add(main,      col=1, row=1)
    layout.add(statusbar, col=0, row=2, colspan=2)
"""

from .flex       import FlexFrame, FlexRow, FlexCol
from .grid_frame import GridFrame
from .spacer     import Spacer
from .responsive import ResponsiveMixin

__all__ = [
    "FlexFrame",
    "FlexRow",
    "FlexCol",
    "GridFrame",
    "Spacer",
    "ResponsiveMixin",
]

__version__ = "0.1.0"
__author__  = "SnakePlayer contributors"
__license__ = "MIT"
