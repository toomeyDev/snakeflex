# snakeflex

**Flexbox and CSS Grid-inspired layout utilities for tkinter and customtkinter.**

`snakeflex` implements Flexbox inspired functionality in the context of building user interfaces with Tkinter and/or CustomTkinter and Python. It works as
a drop-in layout layer over standard `tkinter` and `customtkinter` widgets, without any external
dependencies.
```bash
pip install snakeflex
```

---

## Quick start

```python
import tkinter as tk
from snakeflex import FlexRow, FlexCol, GridFrame, Spacer

root = tk.Tk()

# Horizontal bar
bar = FlexRow(root, justify="space-between", align="center", gap=8)
bar.pack(fill="x")

title = tk.Label(bar, text="My App")
bar.add(title)
bar.add(Spacer())                           # pushes right-hand items to the edge
bar.add(tk.Button(bar, text="Settings"))
bar.add(tk.Button(bar, text="Quit", command=root.quit))

# Vertical panel
panel = FlexCol(root, align="stretch", gap=4)
panel.pack(fill="both", expand=True)

panel.add(tk.Label(panel, text="Header"))
panel.add(tk.Text(panel), grow=1)           # Text widget fills remaining height
panel.add(tk.Label(panel, text="Status"))

root.mainloop()
```

---

## FlexRow / FlexCol

```python
from snakeflex import FlexRow, FlexCol
```

### Parameters

| Parameter   | Type   | Default       | Description |
|-------------|--------|---------------|-------------|
| `justify`   | str    | `"start"`     | Main-axis alignment: `"start"` `"end"` `"center"` `"space-between"` `"space-around"` `"space-evenly"` |
| `align`     | str    | `"stretch"`   | Cross-axis alignment: `"stretch"` `"start"` `"end"` `"center"` |
| `gap`       | int    | `0`           | Pixels of space between children |
| `fg_color`  | str    | `"transparent"` | Background colour (customtkinter-compatible alias for `bg`) |
| `direction` | str    | `"row"`       | `FlexFrame` only: `"row"` `"column"` `"row-reverse"` `"column-reverse"` |

### `.add(widget, *, grow=0, align=None)`

```python
row = FlexRow(parent, justify="space-between", gap=8)
row.add(logo)
row.add(slider, grow=1)      # slider expands to fill spare space
row.add(mute_btn)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `grow`    | `0`     | Proportional share of remaining space (like `flex-grow`) |
| `align`   | `None`  | Per-child cross-axis override |

Returns the widget for chaining.

<hr>>

## GridFrame

```python
from snakeflex import GridFrame
```

### Template syntax

```
"200px 1fr 2fr"  - fixed 200 px | 1 share | 2 shares of remaining space
"1fr 1fr 1fr"    - three equal columns
"auto 1fr"       - content-sized column + fills the rest
"48px 1fr 28px"  - fixed header | flexible content | fixed footer
```

### Usage

```python
layout = GridFrame(parent,
    columns="220px 1fr",
    rows="48px 1fr 28px",
    gap=4,
)
layout.add(topbar,    col=0, row=0, colspan=2)
layout.add(sidebar,   col=0, row=1)
layout.add(content,   col=1, row=1)
layout.add(statusbar, col=0, row=2, colspan=2)
```

### Responsive breakpoints

```python
layout.on_resize(800,
    narrow=lambda: layout.hide_col(2),   # collapse detail panel
    wide=lambda:   layout.show_col(2),
)
```

<hr>

## Spacer

An invisible, expanding spacer — equivalent to `<div style="flex: 1" />`.

```python
bar = FlexRow(parent, justify="start", gap=8)
bar.add(logo)
bar.add(Spacer())      # everything after this is pushed right
bar.add(btn_a)
bar.add(btn_b)
```

When added to a `FlexRow`/`FlexCol`, `Spacer` defaults to `grow=1`.

<br>

## customtkinter compatibility

All containers accept `fg_color` as an alias for `bg` and default to
`"transparent"` so they blend seamlessly into CTk windows:

```python
import customtkinter as ctk
from snakeflex import FlexRow

app = ctk.CTk()
bar = FlexRow(app, fg_color="transparent", gap=8)
bar.add(ctk.CTkLabel(bar, text="Hello"))
bar.add(ctk.CTkButton(bar, text="Go"), grow=1)
```

<hr>

## Installation

```bash
pip install snakeflex
```

