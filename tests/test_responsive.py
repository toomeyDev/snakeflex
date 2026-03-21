"""Tests for ResponsiveMixin."""
import tkinter as tk
import pytest

from snakeflex import GridFrame
from snakeflex.responsive import ResponsiveMixin


@pytest.fixture(scope="module")
def root():
    r = tk.Tk()
    r.withdraw()
    yield r
    r.destroy()


class TestResponsiveMixin:
    def test_on_resize_registers_breakpoint(self, root):
        gf = GridFrame(root, columns="1fr 1fr")
        narrow_called = []
        wide_called   = []
        gf.on_resize(800,
            narrow=lambda: narrow_called.append(1),
            wide=lambda:   wide_called.append(1),
        )
        assert 800 in gf._breakpoints

    def test_multiple_breakpoints(self, root):
        gf = GridFrame(root)
        gf.on_resize(600, narrow=lambda: None)
        gf.on_resize(900, narrow=lambda: None)
        assert len(gf._breakpoints) == 2

    def test_callbacks_are_optional(self, root):
        gf = GridFrame(root)
        # Only narrow, no wide — should not raise
        gf.on_resize(700, narrow=lambda: None)
        gf._check_breakpoints()   # force a check without crashing


class TestResponsiveMixinStandalone:
    """Test ResponsiveMixin applied to a plain tk.Frame."""

    def test_mixin_on_plain_frame(self, root):
        class ResponsiveFrame(ResponsiveMixin, tk.Frame):
            def __init__(self, parent):
                tk.Frame.__init__(self, parent)
                ResponsiveMixin.__init__(self)

        frame = ResponsiveFrame(root)
        calls = []
        frame.on_resize(500, narrow=lambda: calls.append("narrow"))
        assert 500 in frame._rm_breakpoints
