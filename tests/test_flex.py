"""Tests for FlexFrame, FlexRow, FlexCol."""
import tkinter as tk
import pytest

from snakeflex import FlexRow, FlexCol, FlexFrame, Spacer


@pytest.fixture(scope="module")
def root():
    r = tk.Tk()
    r.withdraw()
    yield r
    r.destroy()


# Construction

class TestConstruction:
    def test_flexrow_is_frame(self, root):
        row = FlexRow(root)
        assert isinstance(row, tk.Frame)

    def test_flexcol_is_frame(self, root):
        col = FlexCol(root)
        assert isinstance(col, tk.Frame)

    def test_direction_defaults(self, root):
        assert FlexRow(root)._direction == "row"
        assert FlexCol(root)._direction == "column"

    def test_justify_default(self, root):
        assert FlexRow(root)._justify == "start"

    def test_align_default(self, root):
        assert FlexRow(root)._align == "stretch"

    def test_gap_default(self, root):
        assert FlexRow(root)._gap == 0

    def test_gap_negative_clamped(self, root):
        row = FlexRow(root, gap=-5)
        assert row._gap == 0

    def test_fg_color_accepted(self, root):
        # Should not raise
        FlexRow(root, fg_color="#1e1e2e")
        FlexRow(root, fg_color="transparent")


# .add()

class TestAdd:
    def test_add_returns_widget(self, root):
        row = FlexRow(root)
        btn = tk.Button(row, text="OK")
        result = row.add(btn)
        assert result is btn

    def test_add_registers_child(self, root):
        row = FlexRow(root)
        btn = tk.Button(row, text="OK")
        row.add(btn, grow=1)
        assert len(row._children) == 1
        assert row._children[0].widget is btn
        assert row._children[0].grow == 1

    def test_spacer_defaults_grow_1(self, root):
        row = FlexRow(root)
        sp = Spacer(root)
        row.add(sp)
        assert row._children[0].grow == 1

    def test_spacer_grow_can_be_overridden(self, root):
        row = FlexRow(root)
        sp = Spacer(root)
        row.add(sp, grow=2)
        assert row._children[0].grow == 2

    def test_multiple_adds(self, root):
        row = FlexRow(root)
        for i in range(5):
            row.add(tk.Label(row, text=str(i)))
        assert len(row._children) == 5


# Relayout coalescing

class TestRelayout:
    def test_pending_set_on_add(self, root):
        row = FlexRow(root)
        assert not row._relayout_pending
        row.add(tk.Label(row, text="x"))
        assert row._relayout_pending

    def test_pending_cleared_after_idle(self, root):
        row = FlexRow(root)
        row.add(tk.Label(row, text="x"))
        root.update()   # after(0) is a timer event; update() flushes it
        assert not row._relayout_pending


# Sticky (align) mapping

class TestSticky:
    def test_row_stretch(self, root):
        row = FlexRow(root, align="stretch")
        assert "n" in row._sticky(None) and "s" in row._sticky(None)

    def test_row_start(self, root):
        row = FlexRow(root, align="start")
        assert row._sticky(None) == "n"

    def test_row_end(self, root):
        row = FlexRow(root, align="end")
        assert row._sticky(None) == "s"

    def test_row_center(self, root):
        row = FlexRow(root, align="center")
        assert row._sticky(None) == ""

    def test_col_stretch(self, root):
        col = FlexCol(root, align="stretch")
        assert "e" in col._sticky(None) and "w" in col._sticky(None)

    def test_item_align_overrides_container(self, root):
        row = FlexRow(root, align="stretch")
        assert row._sticky("center") == ""


# Gap padding

class TestGapPadding:
    def test_no_gap(self, root):
        row = FlexRow(root, gap=0)
        assert row._gap_padding(0, 3) == (0, 0)

    def test_single_item_no_gap(self, root):
        row = FlexRow(root, gap=8)
        assert row._gap_padding(0, 1) == (0, 0)

    def test_first_item_gap(self, root):
        row = FlexRow(root, gap=8)
        before, after = row._gap_padding(0, 3)
        assert before == 0 and after == 4

    def test_last_item_gap(self, root):
        row = FlexRow(root, gap=8)
        before, after = row._gap_padding(2, 3)
        assert before == 4 and after == 0

    def test_middle_item_gap(self, root):
        row = FlexRow(root, gap=8)
        before, after = row._gap_padding(1, 3)
        assert before == 4 and after == 4
