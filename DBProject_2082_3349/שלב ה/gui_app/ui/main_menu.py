"""Main navigation hub – sidebar layout with stats bar."""
import tkinter as tk
from tkinter import ttk

from database import DatabaseError, fetch_one, get_existing_tables, test_connection
from table_metadata import TABLE_GROUPS, TABLES
from ui.crud_window import CrudWindow
from ui.queries_window import QueriesWindow
from ui.routines_window import RoutinesWindow
from ui.styles import (
    ACCENT, ACCENT_LT, BG, BG2, BG3, BORDER,
    FONT_BODY, FONT_HEAD, FONT_SMALL, FONT_TITLE, FONT_DISPLAY,
    GUTTER, PAD, PRIMARY, PRIMARY_LT, TEXT, TEXT_DIM, TEXT_MUTED,
    DANGER, SUCCESS, WARNING,
    configure_styles, hline, ScrollableFrame,
)

_SIDEBAR_BG  = "#111e2d"
_SIDEBAR_W   = 220


# ── Group icon map ─────────────────────────────────────────────────────────────
_GROUP_ICONS = {
    "ניהול גן החיות":  "🌿",
    "צוות ופעילויות":  "👥",
    "מחלקה וטרינרית":  "🩺",
    "מערכת (יומנים)":  "📋",
}

_TABLE_ICONS = {
    "HABITAT":               "🏕️",
    "SPECIES":               "🐾",
    "DIETPLAN":              "🥗",
    "ANIMAL":                "🦒",
    "HEALTHRECORD":          "🩺",
    "DAILYFEEDING":          "🍖",
    "EMPLOYEE":              "👷",
    "ACTIVITY_TYPE":         "📌",
    "ACTIVITY":              "🎯",
    "ACTIVITY_EMPLOYEE":     "🔗",
    "ACTIVITY_ANIMAL":       "🔗",
    "VETERINARIAN":          "👨‍⚕️",
    "MEDICALVISIT":          "🏥",
    "TREATMENT":             "💊",
    "MEDICATION":            "💉",
    "VACCINATION":           "🛡️",
    "MIRSHAM_VISIT_TREATMENT": "🔗",
    "HERGEL_TREATMENT_MEDICATION": "🔗",
    "TREATMENT_VACCINATION": "🔗",
    "HABITAT_CAPACITY_LOG":  "📊",
}


class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🦁 מערכת ניהול גן החיות – Zoo Management")
        self.configure(bg=BG)

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(sw, 1200), min(sh, 800)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.minsize(900, 600)
        configure_styles(self)

        # Load DB state
        try:
            self._existing_tables = get_existing_tables()
            conn_msg = test_connection()
            self._db_ok = True
        except DatabaseError as exc:
            self._existing_tables = set()
            conn_msg = str(exc)
            self._db_ok = False

        self._build_layout(conn_msg)

    # ── Top-level layout ──────────────────────────────────────────────────────
    def _build_layout(self, conn_msg: str):
        # Header bar
        self._build_header(conn_msg)

        # Body = sidebar + content
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(body)
        self._build_content(body)

        # Footer
        self._build_footer()

    def _build_header(self, conn_msg: str):
        hdr = tk.Frame(self, bg=_SIDEBAR_BG, height=58)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Left: logo
        logo_f = tk.Frame(hdr, bg=PRIMARY, width=_SIDEBAR_W)
        logo_f.pack(side=tk.RIGHT, fill=tk.Y)
        logo_f.pack_propagate(False)
        tk.Label(logo_f, text="🦁  Zoo Management",
                 bg=PRIMARY, fg="white", font=FONT_HEAD,
                 anchor="center").pack(fill=tk.BOTH, expand=True)

        # Right: DB status
        status_f = tk.Frame(hdr, bg=_SIDEBAR_BG)
        status_f.pack(side=tk.LEFT, fill=tk.Y, padx=PAD)

        dot_color = SUCCESS if self._db_ok else DANGER
        dot = tk.Canvas(status_f, width=10, height=10, bg=_SIDEBAR_BG,
                        highlightthickness=0)
        dot.create_oval(1, 1, 9, 9, fill=dot_color, outline="")
        dot.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(status_f, text=conn_msg[:72],
                 bg=_SIDEBAR_BG, fg=TEXT_MUTED, font=FONT_SMALL).pack(side=tk.LEFT)

        # Action buttons in header
        btn_f = tk.Frame(hdr, bg=_SIDEBAR_BG)
        btn_f.pack(side=tk.LEFT, fill=tk.Y, padx=PAD * 2)

        _HeaderBtn(btn_f, text="📊  שאילתות", bg=BG2,
                   command=lambda: QueriesWindow(self)).pack(side=tk.LEFT, padx=4, pady=10)
        _HeaderBtn(btn_f, text="⚙️  פרוצדורות", bg=BG2,
                   command=lambda: RoutinesWindow(self)).pack(side=tk.LEFT, padx=4, pady=10)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=_SIDEBAR_BG, width=_SIDEBAR_W)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Section header
        tk.Label(sidebar, text="טבלאות המערכת",
                 bg=_SIDEBAR_BG, fg=TEXT_DIM, font=FONT_SMALL,
                 anchor="e").pack(fill=tk.X, padx=PAD, pady=(14, 6))

        # Scrollable inner area
        sf = ScrollableFrame(sidebar, bg=_SIDEBAR_BG)
        sf.pack(fill=tk.BOTH, expand=True)
        inner = sf.inner

        for group_name, table_keys in TABLE_GROUPS.items():
            visible = [k for k in table_keys
                       if TABLES[k].table.lower() in self._existing_tables]
            if not visible:
                continue

            icon = _GROUP_ICONS.get(group_name, "📁")
            grp_lbl = tk.Label(inner,
                               text=f"  {icon}  {group_name}",
                               bg=_SIDEBAR_BG, fg=ACCENT, font=FONT_SMALL,
                               anchor="e")
            grp_lbl.pack(fill=tk.X, padx=6, pady=(10, 2))

            for key in visible:
                tdef = TABLES[key]
                t_icon = _TABLE_ICONS.get(key, "•")
                btn = _SidebarBtn(inner,
                                  text=f"  {t_icon}  {tdef.display_name}",
                                  command=lambda k=key: CrudWindow(self, TABLES[k]))
                btn.pack(fill=tk.X, padx=6, pady=1)

    def _build_content(self, parent):
        content = tk.Frame(parent, bg=BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Stats strip
        self._build_stats(content)

        # Welcome banner
        self._build_banner(content)

    def _build_stats(self, parent):
        strip = tk.Frame(parent, bg=BG3, height=50)
        strip.pack(fill=tk.X)
        strip.pack_propagate(False)

        stats = self._collect_stats()
        for label, value, color in stats:
            f = tk.Frame(strip, bg=BG3)
            f.pack(side=tk.RIGHT, padx=PAD * 2, pady=8)
            tk.Label(f, text=str(value), bg=BG3, fg=color,
                     font=FONT_HEAD).pack()
            tk.Label(f, text=label, bg=BG3, fg=TEXT_MUTED,
                     font=FONT_SMALL).pack()

    def _collect_stats(self):
        stats = []
        quick_counts = [
            ("animal",       "חיות",     PRIMARY_LT),
            ("veterinarian", "וטרינרים", ACCENT),
            ("employee",     "עובדים",   "#1e90ff"),
            ("medicalvisit", "ביקורים",  "#a29bfe"),
        ]
        for tbl, label, color in quick_counts:
            if tbl in self._existing_tables:
                try:
                    row = fetch_one(f"SELECT COUNT(*) FROM {tbl}")
                    val = int(row[0]) if row else 0
                except DatabaseError:
                    val = "–"
            else:
                val = "–"
            stats.append((label, val, color))
        return stats

    def _build_banner(self, parent):
        # Scrollable main content area with table cards
        sf = ScrollableFrame(parent)
        sf.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=PAD)
        inner = sf.inner

        # Welcome text
        welcome = tk.Frame(inner, bg=BG)
        welcome.pack(fill=tk.X, pady=(8, 16))
        tk.Label(welcome, text="ברוכים הבאים למערכת ניהול גן החיות",
                 bg=BG, fg=PRIMARY_LT, font=FONT_TITLE, anchor="e").pack(anchor="e")
        tk.Label(welcome, text="בחרו טבלה מהסרגל הצדדי, או השתמשו בכרטיסיות להלן",
                 bg=BG, fg=TEXT_MUTED, font=FONT_SMALL, anchor="e").pack(anchor="e")

        # Table-group cards
        for group_name, table_keys in TABLE_GROUPS.items():
            visible = [k for k in table_keys
                       if TABLES[k].table.lower() in self._existing_tables]
            if not visible:
                continue

            # Group card
            card = tk.Frame(inner, bg=BG2, highlightbackground=BORDER,
                            highlightthickness=1)
            card.pack(fill=tk.X, pady=6)

            icon = _GROUP_ICONS.get(group_name, "📁")
            hdr = tk.Frame(card, bg=BG3)
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=f"  {icon}  {group_name}",
                     bg=BG3, fg=ACCENT, font=FONT_HEAD,
                     anchor="e", pady=8, padx=PAD).pack(anchor="e")

            # Table button grid
            btn_grid = tk.Frame(card, bg=BG2, padx=PAD, pady=PAD)
            btn_grid.pack(fill=tk.X)

            for col_idx, key in enumerate(visible):
                tdef = TABLES[key]
                t_icon = _TABLE_ICONS.get(key, "•")
                _TableCard(btn_grid, icon=t_icon, name=tdef.display_name,
                           command=lambda k=key: CrudWindow(self, TABLES[k]),
                           exists=(tdef.table.lower() in self._existing_tables),
                           ).grid(row=0, column=col_idx, padx=4, pady=4, sticky="nsew")

            # Make columns equal-width
            for ci in range(len(visible)):
                btn_grid.columnconfigure(ci, weight=1)

        if not self._existing_tables:
            msg = tk.Label(inner,
                           text="⚠️  לא נמצאו טבלאות. ודאו חיבור ל-zoo_db והריצו את סקריפטי שלב א'.",
                           bg=BG, fg=DANGER, font=FONT_BODY,
                           wraplength=600, justify="right")
            msg.pack(pady=40)

    def _build_footer(self):
        foot = tk.Frame(self, bg=_SIDEBAR_BG, height=30)
        foot.pack(fill=tk.X, side=tk.BOTTOM)
        foot.pack_propagate(False)
        tk.Label(foot,
                 text="שלב ה'  |  Yuval Schmidt & Yedidya Bar-Gad  |  PostgreSQL + Python/Tkinter",
                 bg=_SIDEBAR_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side=tk.LEFT, padx=PAD)


# ── Helper widgets ────────────────────────────────────────────────────────────

class _SidebarBtn(tk.Label):
    """Sidebar navigation item."""
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent, text=text, bg=_SIDEBAR_BG, fg=TEXT_MUTED,
                         font=FONT_SMALL, anchor="e", pady=5, padx=8,
                         cursor="hand2", **kw)
        self._cmd = command
        self.bind("<Enter>", lambda _: self.configure(bg=BG3, fg=PRIMARY_LT))
        self.bind("<Leave>", lambda _: self.configure(bg=_SIDEBAR_BG, fg=TEXT_MUTED))
        self.bind("<Button-1>", lambda _: command())


class _HeaderBtn(tk.Label):
    """Compact button for the header bar."""
    def __init__(self, parent, text, command, bg=BG2, **kw):
        super().__init__(parent, text=text, bg=bg, fg=TEXT,
                         font=FONT_SMALL, padx=10, pady=5,
                         cursor="hand2", relief="flat", **kw)
        self.bind("<Enter>", lambda _: self.configure(bg=PRIMARY, fg="white"))
        self.bind("<Leave>", lambda _: self.configure(bg=bg, fg=TEXT))
        self.bind("<Button-1>", lambda _: command())


class _TableCard(tk.Frame):
    """Clickable card for a single table in the content area."""
    def __init__(self, parent, icon, name, command, exists=True, **kw):
        bg = BG2 if exists else BG3
        super().__init__(parent, bg=bg, highlightbackground=BORDER,
                         highlightthickness=1, cursor="hand2" if exists else "", **kw)
        tk.Label(self, text=icon, bg=bg, font=("Segoe UI", 18)).pack(pady=(8, 2))
        tk.Label(self, text=name, bg=bg, fg=TEXT if exists else TEXT_DIM,
                 font=FONT_SMALL, wraplength=130, justify="center").pack(padx=6, pady=(0, 8))
        if exists:
            self.bind("<Enter>", lambda _: self._hover(True))
            self.bind("<Leave>", lambda _: self._hover(False))
            self.bind("<Button-1>", lambda _: command())
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda _: command())
                child.bind("<Enter>", lambda _: self._hover(True))
                child.bind("<Leave>", lambda _: self._hover(False))

    def _hover(self, on: bool):
        color = BG3 if on else BG2
        self.configure(bg=color, highlightbackground=PRIMARY if on else BORDER)
        for child in self.winfo_children():
            child.configure(bg=color)
