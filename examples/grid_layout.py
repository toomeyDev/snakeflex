"""CSS Grid-style layout demo using GridFrame.

Run with:  python examples/grid_layout.py
"""
import tkinter as tk
from snakeflex import GridFrame, FlexRow, Spacer

root = tk.Tk()
root.title("snakeflex — GridFrame demo")
root.geometry("800x500")
root.configure(bg="#1e1e2e")

# Root grid: sidebar | main, with fixed header and footer 
layout = GridFrame(root,
    columns="200px 1fr",
    rows="44px 1fr 32px",
    gap=0,
)
layout.pack(fill="both", expand=True)

# Top bar (spans both columns) 
topbar = FlexRow(layout, justify="space-between", align="center",
                  gap=8, bg="#11111b")
layout.add(topbar, col=0, row=0, colspan=2)

topbar.add(tk.Label(topbar, text="  GridFrame Demo",
                     bg="#11111b", fg="#cdd6f4", font=("Helvetica", 12, "bold")))
topbar.add(Spacer(topbar))
topbar.add(tk.Button(topbar, text="Quit", bg="#11111b", fg="#f38ba8",
                      relief="flat", padx=8, command=root.quit))

# Sidebar 
sidebar = tk.Frame(layout, bg="#181825")
layout.add(sidebar, col=0, row=1)

for text in ("Dashboard", "Library", "Playlists", "Settings"):
    tk.Button(sidebar, text=text, bg="#181825", fg="#cdd6f4",
              activebackground="#313244", relief="flat",
              anchor="w", padx=16, pady=8, width=20
              ).pack(fill="x")

# Main content 
main = tk.Frame(layout, bg="#1e1e2e")
layout.add(main, col=1, row=1)

tk.Label(main, text="Main Content Area", bg="#1e1e2e", fg="#cdd6f4",
          font=("Helvetica", 16)).pack(expand=True)

# Status bar (spans both columns) 
statusbar = FlexRow(layout, justify="start", align="center",
                     gap=16, bg="#11111b")
layout.add(statusbar, col=0, row=2, colspan=2)

statusbar.add(tk.Label(statusbar, text="  Ready", bg="#11111b",
                         fg="#6c7086", font=("Helvetica", 9)))
statusbar.add(Spacer(statusbar))
statusbar.add(tk.Label(statusbar, text="42 tracks  ", bg="#11111b",
                         fg="#6c7086", font=("Helvetica", 9)))

# Responsive: collapse sidebar below 600px 
layout.on_resize(600,
    narrow=lambda: layout.hide_col(0),
    wide=lambda:   layout.show_col(0),
)

root.mainloop()
