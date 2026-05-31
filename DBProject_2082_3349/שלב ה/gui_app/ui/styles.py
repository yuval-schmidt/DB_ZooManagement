"""Shared Tkinter dark-mode design system for Zoo Management GUI."""
import tkinter as tk
from tkinter import ttk

# ─── Color Palette ───────────────────────────────────────────────────────────
BG          = "#0f1923"   # deepest background
BG2         = "#1a2535"   # card / panel background
BG3         = "#222f42"   # elevated surface (e.g. toolbar)
BORDER      = "#2e3f58"   # subtle separator / border
PRIMARY     = "#00c896"   # emerald green – primary action
PRIMARY_DK  = "#00a07a"   # pressed / hover darker
PRIMARY_LT  = "#00dfa8"   # lighter tint for text on dark
ACCENT      = "#f0a500"   # gold accent
ACCENT_LT   = "#ffc84a"   # lighter gold
DANGER      = "#ff4757"   # destructive action
DANGER_DK   = "#cc3344"
SUCCESS     = "#2ed573"   # success indicator
WARNING     = "#ffa502"   # warning
INFO        = "#1e90ff"   # informational blue
TEXT        = "#e8edf5"   # primary text
TEXT_MUTED  = "#7a8ea8"   # secondary / muted text
TEXT_DIM    = "#4a5c72"   # very dim – hints
CARD        = BG2
TREEVIEW_ODD  = "#1f2f44"
TREEVIEW_EVEN = "#1a2535"
TREEVIEW_SEL  = "#003d30"
TREEVIEW_SEL_FG = PRIMARY_LT

# ─── Typography ──────────────────────────────────────────────────────────────
FONT_DISPLAY = ("Segoe UI", 20, "bold")
FONT_TITLE   = ("Segoe UI", 14, "bold")
FONT_HEAD    = ("Segoe UI", 11, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)

# ─── Sizing ──────────────────────────────────────────────────────────────────
RADIUS  = 10   # corner radius for rounded widgets
PAD     = 12   # standard padding
GUTTER  = 8    # half-gutter


def configure_styles(root):
    """Apply the dark-mode ttk style theme to *root*."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # ── Base frames & labels ────────────────────────────────────────────────
    style.configure("TFrame",       background=BG)
    style.configure("Card.TFrame",  background=BG2)
    style.configure("Dark.TFrame",  background=BG3)
    style.configure("Sidebar.TFrame", background="#111e2d")

    style.configure("TLabel",        background=BG,   foreground=TEXT,       font=FONT_BODY)
    style.configure("Card.TLabel",   background=BG2,  foreground=TEXT,       font=FONT_BODY)
    style.configure("Dark.TLabel",   background=BG3,  foreground=TEXT,       font=FONT_BODY)
    style.configure("Sidebar.TLabel",background="#111e2d", foreground=TEXT_MUTED, font=FONT_SMALL)
    style.configure("Title.TLabel",  background=BG,   foreground=PRIMARY_LT, font=FONT_TITLE)
    style.configure("Head.TLabel",   background=BG,   foreground=TEXT,       font=FONT_HEAD)
    style.configure("Muted.TLabel",  background=BG,   foreground=TEXT_MUTED, font=FONT_SMALL)
    style.configure("Card.Muted.TLabel",background=BG2,foreground=TEXT_MUTED,font=FONT_SMALL)
    style.configure("Accent.TLabel", background=BG,   foreground=ACCENT,     font=FONT_HEAD)
    style.configure("Success.TLabel",background=BG2,  foreground=SUCCESS,    font=FONT_BODY)
    style.configure("Danger.TLabel", background=BG,   foreground=DANGER,     font=FONT_BODY)

    # ── Buttons ─────────────────────────────────────────────────────────────
    _btn_base = dict(font=FONT_BODY, padding=(10, 7), relief="flat", borderwidth=0)

    style.configure("Primary.TButton",
                    foreground="white", background=PRIMARY,
                    **_btn_base)
    style.map("Primary.TButton",
              background=[("active", PRIMARY_DK), ("pressed", PRIMARY_DK)],
              foreground=[("active", "white")])

    style.configure("Accent.TButton",
                    foreground=BG, background=ACCENT,
                    **_btn_base)
    style.map("Accent.TButton",
              background=[("active", ACCENT_LT), ("pressed", ACCENT_LT)])

    style.configure("Danger.TButton",
                    foreground="white", background=DANGER,
                    **_btn_base)
    style.map("Danger.TButton",
              background=[("active", DANGER_DK), ("pressed", DANGER_DK)])

    style.configure("Ghost.TButton",
                    foreground=TEXT_MUTED, background=BG3,
                    **_btn_base)
    style.map("Ghost.TButton",
              foreground=[("active", TEXT)],
              background=[("active", BORDER)])

    style.configure("TButton",
                    foreground=TEXT, background=BG3,
                    **_btn_base)
    style.map("TButton",
              background=[("active", BORDER)],
              foreground=[("active", TEXT)])

    # ── Entries ─────────────────────────────────────────────────────────────
    style.configure("TEntry",
                    fieldbackground=BG3,
                    foreground=TEXT,
                    insertcolor=PRIMARY,
                    bordercolor=BORDER,
                    lightcolor=BG3,
                    darkcolor=BG3,
                    font=FONT_BODY,
                    padding=6)
    style.map("TEntry",
              bordercolor=[("focus", PRIMARY), ("hover", PRIMARY_DK)],
              fieldbackground=[("disabled", BG2)])

    # ── Combobox ────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=BG3,
                    foreground=TEXT,
                    background=BG3,
                    arrowcolor=PRIMARY,
                    bordercolor=BORDER,
                    lightcolor=BG3,
                    darkcolor=BG3,
                    font=FONT_BODY,
                    padding=5)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG3)],
              bordercolor=[("focus", PRIMARY)])
    root.option_add("*TCombobox*Listbox.background", BG2)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", "white")

    # ── Treeview ────────────────────────────────────────────────────────────
    style.configure("Treeview",
                    background=TREEVIEW_ODD,
                    foreground=TEXT,
                    fieldbackground=TREEVIEW_ODD,
                    borderwidth=0,
                    relief="flat",
                    rowheight=30,
                    font=FONT_BODY)
    style.map("Treeview",
              background=[("selected", TREEVIEW_SEL)],
              foreground=[("selected", TREEVIEW_SEL_FG)])
    style.configure("Treeview.Heading",
                    background=BG3,
                    foreground=PRIMARY_LT,
                    font=FONT_HEAD,
                    relief="flat",
                    borderwidth=0,
                    padding=(8, 6))
    style.map("Treeview.Heading",
              background=[("active", BG3)])

    # ── Notebook ────────────────────────────────────────────────────────────
    style.configure("TNotebook",
                    background=BG,
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=BG2,
                    foreground=TEXT_MUTED,
                    font=FONT_BODY,
                    padding=[14, 8],
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", BG3), ("active", BG3)],
              foreground=[("selected", PRIMARY_LT), ("active", TEXT)])

    # ── Scrollbar ────────────────────────────────────────────────────────────
    style.configure("TScrollbar",
                    background=BG2,
                    troughcolor=BG,
                    bordercolor=BG,
                    arrowcolor=TEXT_DIM,
                    gripcount=0,
                    relief="flat")
    style.map("TScrollbar",
              background=[("active", BORDER)])

    # ── Separator ───────────────────────────────────────────────────────────
    style.configure("TSeparator", background=BORDER)

    # ── LabelFrame ──────────────────────────────────────────────────────────
    style.configure("TLabelframe",
                    background=BG2,
                    bordercolor=BORDER,
                    relief="solid",
                    borderwidth=1)
    style.configure("TLabelframe.Label",
                    background=BG2,
                    foreground=ACCENT,
                    font=FONT_HEAD)

    # Set default root background
    root.configure(bg=BG)


# ─── Utility: alternating Treeview rows ──────────────────────────────────────
def tag_treeview_rows(tree: "ttk.Treeview"):
    """Apply alternating row tags after populating a Treeview."""
    tree.tag_configure("odd",  background=TREEVIEW_ODD)
    tree.tag_configure("even", background=TREEVIEW_EVEN)
    for i, iid in enumerate(tree.get_children()):
        tree.item(iid, tags=("even" if i % 2 == 0 else "odd",))


# ─── Utility: status-dot label ───────────────────────────────────────────────
def make_status_dot(parent, color: str, text: str, bg: str = BG) -> tk.Frame:
    """Return a tiny frame with a colored circle + label."""
    f = tk.Frame(parent, bg=bg)
    dot = tk.Canvas(f, width=10, height=10, bg=bg, highlightthickness=0)
    dot.create_oval(1, 1, 9, 9, fill=color, outline="")
    dot.pack(side=tk.LEFT, padx=(0, 5))
    tk.Label(f, text=text, bg=bg, fg=TEXT_MUTED, font=FONT_SMALL).pack(side=tk.LEFT)
    return f


# ─── Utility: horizontal rule ─────────────────────────────────────────────────
def hline(parent, bg=BORDER, pady=6) -> tk.Frame:
    f = tk.Frame(parent, height=1, bg=bg)
    f.pack(fill=tk.X, pady=pady)
    return f


# ─── Utility: section header label ───────────────────────────────────────────
def section_label(parent, text: str, bg=BG2) -> tk.Label:
    lbl = tk.Label(
        parent, text=text, bg=bg, fg=PRIMARY_LT,
        font=FONT_HEAD, anchor="e",
    )
    lbl.pack(fill=tk.X, padx=PAD, pady=(PAD, 4))
    return lbl


# ─── Animated hover button (pure tk) ─────────────────────────────────────────
class HoverButton(tk.Button):
    """A tk.Button that changes colour on hover."""

    def __init__(self, parent, normal_bg=BG3, hover_bg=PRIMARY,
                 normal_fg=TEXT, hover_fg="white", **kw):
        kw.setdefault("relief", "flat")
        kw.setdefault("cursor", "hand2")
        kw.setdefault("borderwidth", 0)
        kw.setdefault("activebackground", hover_bg)
        kw.setdefault("activeforeground", hover_fg)
        kw.setdefault("font", FONT_BODY)
        super().__init__(parent, bg=normal_bg, fg=normal_fg, **kw)
        self._nbg = normal_bg
        self._hbg = hover_bg
        self._nfg = normal_fg
        self._hfg = hover_fg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e=None):
        self.configure(bg=self._hbg, fg=self._hfg)

    def _on_leave(self, _e=None):
        self.configure(bg=self._nbg, fg=self._nfg)


# ─── Scrollable frame helper ─────────────────────────────────────────────────
class ScrollableFrame(tk.Frame):
    """A tk.Frame with a vertical scrollbar; child widgets go into .inner."""

    def __init__(self, parent, bg=BG, **kw):
        super().__init__(parent, bg=bg, **kw)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = tk.Frame(canvas, bg=bg)
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def _cfg(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _resize(e):
            canvas.itemconfig(win, width=e.width)

        self.inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", _resize)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _scroll)
