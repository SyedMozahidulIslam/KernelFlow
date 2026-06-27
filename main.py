"""
main.py
=======
KernelFlow — CPU Scheduling Simulator by SMI Fahim
Entry point. Creates the Tk root and launches MainWindow.

Usage:
    python main.py
"""

import tkinter as tk
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import MainWindow


def main():
    root = tk.Tk()

    # ── DPI awareness (Windows) ───────────────────
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass   # Not Windows — safe to ignore

    # ── Launch ────────────────────────────────────
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
