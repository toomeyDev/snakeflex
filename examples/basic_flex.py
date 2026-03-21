"""Basic FlexRow / FlexCol demo.

Run with:  python examples/basic_flex.py
"""
import tkinter as tk
from snakeflex import FlexRow, FlexCol, Spacer

root = tk.Tk()
root.title("snakeflex — basic flex demo")
root.geometry("640x400")
root.configure(bg="#1e1e2e")


# ── Top bar ────────────────────────────────────────────────────────────────────
bar = FlexRow(root, justify="space-between", align="center", gap=8, bg="#181825")
bar.pack(fill="x", padx=0, pady=0)

bar.add(tk.Label(bar, text="  SnakeFlex Demo", bg="#181825", fg="#cdd6f4",
                  font=("Helvetica", 14, "bold")))
bar.add(Spacer(bar))
bar.add(tk.Button(bar, text="Settings", bg="#313244", fg="#cdd6f4",
                   relief="flat", padx=8))
bar.add(tk.Button(bar, text="✕", bg="#181825", fg="#f38ba8",
                   relief="flat", padx=8, command=root.quit))


# ── Main layout ───────────────────────────────────────────────────────────────
body = FlexRow(root, align="stretch", gap=0, bg="#1e1e2e")
body.pack(fill="both", expand=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar = FlexCol(body, align="stretch", gap=4, bg="#181825", width=180)
sidebar.pack_propagate(False)
body.add(sidebar)

for label in ("Library", "Artists", "Albums", "Playlists", "Queue"):
    btn = tk.Button(sidebar, text=label, bg="#181825", fg="#cdd6f4",
                    activebackground="#313244", relief="flat",
                    anchor="w", padx=12, pady=6)
    sidebar.add(btn)
sidebar.add(Spacer(sidebar))     # pushes nav items up


# ── Content ───────────────────────────────────────────────────────────────────
content = FlexCol(body, align="stretch", gap=0, bg="#1e1e2e")
body.add(content, grow=1)

# Header row inside content
header = FlexRow(content, justify="space-between", align="center",
                  gap=8, bg="#1e1e2e")
content.add(header)

header.add(tk.Label(header, text="All Songs", bg="#1e1e2e", fg="#cdd6f4",
                     font=("Helvetica", 12, "bold")))
header.add(Spacer(header))
header.add(tk.Button(header, text="+ Add Files", bg="#cba6f7", fg="#1e1e2e",
                      relief="flat", padx=8))

# Track list
track_list = tk.Listbox(content, bg="#181825", fg="#cdd6f4",
                          selectbackground="#313244", relief="flat",
                          font=("Helvetica", 11), borderwidth=0)
for i in range(1, 16):
    track_list.insert("end", f"  Track {i:02d}  —  Artist Name  —  3:42")
content.add(track_list, grow=1)


# ── Player bar ────────────────────────────────────────────────────────────────
player = FlexRow(root, justify="space-between", align="center",
                  gap=12, bg="#181825")
player.pack(fill="x")

player.add(tk.Label(player, text="♫  Now Playing — Track 01",
                     bg="#181825", fg="#a6e3a1", font=("Helvetica", 10)))
player.add(Spacer(player))

controls = FlexRow(player, justify="center", align="center", gap=8, bg="#181825")
player.add(controls)
for symbol in ("⏮", "⏸", "⏭"):
    controls.add(tk.Button(controls, text=symbol, bg="#313244", fg="#cdd6f4",
                            relief="flat", width=3, font=("Helvetica", 13)))

player.add(Spacer(player))
player.add(tk.Label(player, text="Vol ░░░░░░░░", bg="#181825", fg="#6c7086",
                     font=("Courier", 9)))


root.mainloop()
