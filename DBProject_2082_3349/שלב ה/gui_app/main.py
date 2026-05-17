#!/usr/bin/env python3
"""Zoo Management GUI – Phase E entry point."""
import sys
from pathlib import Path

# Ensure gui_app root is on path when run from any directory
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import tkinter as tk

from ui.connection_dialog import ConnectionDialog
from ui.main_menu import MainMenu
from ui.styles import configure_styles


def main():
    root = tk.Tk()
    root.withdraw()
    configure_styles(root)

    def open_menu():
        root.destroy()
        app = MainMenu()
        app.mainloop()

    ConnectionDialog(root, open_menu)
    root.mainloop()


if __name__ == "__main__":
    main()
