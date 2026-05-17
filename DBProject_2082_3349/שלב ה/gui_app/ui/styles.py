"""Shared Tkinter styling."""
import tkinter as tk

BG = "#f0f4f8"
CARD = "#ffffff"
PRIMARY = "#1a5f4a"
PRIMARY_HOVER = "#247a61"
ACCENT = "#e8a838"
TEXT = "#1e293b"
MUTED = "#64748b"
DANGER = "#c0392b"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_HEAD = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)


def configure_styles(root):
    import tkinter.ttk as ttk

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tkinter.TclError:
        pass

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BODY)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=FONT_BODY)
    style.configure("Title.TLabel", background=BG, foreground=PRIMARY, font=FONT_TITLE)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SMALL)
    style.configure(
        "Primary.TButton",
        font=FONT_HEAD,
        padding=(12, 8),
        background=PRIMARY,
        foreground="white",
    )
    style.map("Primary.TButton", background=[("active", PRIMARY_HOVER)])
    style.configure("Treeview", font=FONT_BODY, rowheight=26)
    style.configure("Treeview.Heading", font=FONT_HEAD, background=PRIMARY, foreground="white")
    style.configure("TNotebook", background=BG)
    style.configure("TNotebook.Tab", font=FONT_BODY, padding=[12, 6])
