"""Tests for GridFrame and track parser."""
import tkinter as tk
import pytest

from snakeflex import GridFrame
from snakeflex.grid_frame import _parse_template, _Track


# Track parser

class TestParseTemplate:
    def test_fr(self):
        tracks = _parse_template("1fr")
        assert len(tracks) == 1
        assert tracks[0].kind == "fr"
        assert tracks[0].value == 1.0

    def test_px(self):
        tracks = _parse_template("200px")
        assert tracks[0].kind == "px"
        assert tracks[0].value == 200.0

    def test_auto(self):
        tracks = _parse_template("auto")
        assert tracks[0].kind == "auto"

    def test_mixed(self):
        tracks = _parse_template("200px 1fr 2fr auto")
        kinds = [t.kind for t in tracks]
        assert kinds == ["px", "fr", "fr", "auto"]

    def test_fractional_fr(self):
        tracks = _parse_template("1.5fr")
        assert tracks[0].value == 1.5

    def test_unknown_token_raises(self):
        with pytest.raises(ValueError, match="unknown track token"):
            _parse_template("1em")

    def test_whitespace_tolerance(self):
        tracks = _parse_template("  1fr   2fr  ")
        assert len(tracks) == 2


# GridFrame construction

@pytest.fixture(scope="module")
def root():
    r = tk.Tk()
    r.withdraw()
    yield r
    r.destroy()


class TestGridFrameConstruction:
    def test_is_frame(self, root):
        gf = GridFrame(root)
        assert isinstance(gf, tk.Frame)

    def test_default_single_track(self, root):
        gf = GridFrame(root)
        assert len(gf._col_tracks) == 1
        assert len(gf._row_tracks) == 1

    def test_custom_columns(self, root):
        gf = GridFrame(root, columns="220px 1fr")
        assert len(gf._col_tracks) == 2
        assert gf._col_tracks[0].kind == "px"
        assert gf._col_tracks[1].kind == "fr"

    def test_gap_clamped(self, root):
        gf = GridFrame(root, gap=-1)
        assert gf._gap == 0

    def test_fg_color_accepted(self, root):
        GridFrame(root, fg_color="#1e1e2e")
        GridFrame(root, fg_color="transparent")


# .add()

class TestGridFrameAdd:
    def test_add_returns_widget(self, root):
        gf = GridFrame(root)
        lbl = tk.Label(gf, text="x")
        assert gf.add(lbl) is lbl

    def test_add_registers_cell(self, root):
        gf = GridFrame(root)
        lbl = tk.Label(gf, text="x")
        gf.add(lbl, col=1, row=2, colspan=3, rowspan=2)
        cell = gf._cells[-1]
        assert cell.col == 1
        assert cell.row == 2
        assert cell.colspan == 3
        assert cell.rowspan == 2

    def test_add_triggers_relayout(self, root):
        gf = GridFrame(root)
        lbl = tk.Label(gf, text="x")
        gf.add(lbl)
        assert gf._relayout_pending


# Column/row visibility

class TestVisibility:
    def test_hide_col_sets_hidden(self, root):
        gf = GridFrame(root, columns="1fr 1fr 1fr")
        gf.hide_col(1)
        assert gf._col_tracks[1].hidden is True

    def test_show_col_clears_hidden(self, root):
        gf = GridFrame(root, columns="1fr 1fr 1fr")
        gf.hide_col(1)
        gf.show_col(1)
        assert gf._col_tracks[1].hidden is False

    def test_hide_out_of_range_no_error(self, root):
        gf = GridFrame(root, columns="1fr")
        gf.hide_col(99)   # should not raise

    def test_hide_row_sets_hidden(self, root):
        gf = GridFrame(root, rows="1fr 1fr")
        gf.hide_row(0)
        assert gf._row_tracks[0].hidden is True
