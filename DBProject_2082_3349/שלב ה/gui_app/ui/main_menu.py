"""Main navigation hub (login screen)."""
import tkinter as tk
from tkinter import ttk

from database import DatabaseError, get_existing_tables, test_connection
from table_metadata import TABLE_GROUPS, TABLES
from ui.crud_window import CrudWindow
from ui.queries_window import QueriesWindow
from ui.routines_window import RoutinesWindow
from ui.styles import ACCENT, BG, FONT_BODY, FONT_HEAD, FONT_TITLE, MUTED, PRIMARY, configure_styles


class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("מערכת ניהול גן החיות – Zoo Management")
        self.configure(bg=BG)
        self.geometry("780x680")
        self.minsize(700, 560)
        configure_styles(self)

        try:
            self._existing_tables = get_existing_tables()
            conn_msg = test_connection()
        except DatabaseError as exc:
            self._existing_tables = set()
            conn_msg = f"שגיאת חיבור: {exc}"

        banner = tk.Frame(self, bg=PRIMARY, height=100)
        banner.pack(fill=tk.X)
        banner.pack_propagate(False)
        tk.Label(
            banner, text="🦁 מערכת ניהול גן החיות",
            bg=PRIMARY, fg="white", font=FONT_TITLE,
        ).pack(side=tk.RIGHT, padx=24, pady=28)
        tk.Label(
            banner, text="Zoo Animal Management System",
            bg=PRIMARY, fg=ACCENT, font=FONT_BODY,
        ).pack(side=tk.RIGHT, padx=8)

        body = ttk.Frame(self, padding=16)
        body.pack(fill=tk.BOTH, expand=True)

        ttk.Label(body, text="תפריט ראשי", style="Title.TLabel").pack(anchor=tk.E, pady=(0, 4))
        self.status_label = ttk.Label(body, text=conn_msg, style="Muted.TLabel")
        self.status_label.pack(anchor=tk.E, pady=(0, 12))

        actions = ttk.Frame(body)
        actions.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(
            actions, text="📊 שאילתות שלב ב'", style="Primary.TButton",
            command=lambda: QueriesWindow(self),
        ).pack(side=tk.RIGHT, padx=6)
        ttk.Button(
            actions, text="⚙ פונקציות ופרוצדורות שלב ד'", style="Primary.TButton",
            command=lambda: RoutinesWindow(self),
        ).pack(side=tk.RIGHT, padx=6)

        ttk.Separator(body).pack(fill=tk.X, pady=6)
        ttk.Label(body, text="ניהול טבלאות (CRUD)", font=FONT_HEAD).pack(anchor=tk.E, pady=4)

        # Scrollable table buttons (fixed layout – anchor nw + width binding)
        scroll_outer = ttk.Frame(body)
        scroll_outer.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_outer, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)

        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for group_name, table_keys in TABLE_GROUPS.items():
            visible_keys = [
                k for k in table_keys
                if TABLES[k].table.lower() in self._existing_tables
            ]
            if not visible_keys:
                continue
            gf = ttk.LabelFrame(inner, text=group_name, padding=10)
            gf.pack(fill=tk.X, pady=6, padx=4)

            btn_row = ttk.Frame(gf)
            btn_row.pack(fill=tk.X)
            for key in visible_keys:
                tdef = TABLES[key]
                ttk.Button(
                    btn_row,
                    text=tdef.display_name,
                    command=lambda k=key: CrudWindow(self, TABLES[k]),
                ).pack(side=tk.RIGHT, padx=4, pady=3)

        if not self._existing_tables:
            ttk.Label(
                inner,
                text="לא נמצאו טבלאות – ודאו חיבור ל-zoo_db והריצו את סקריפטי שלב א'",
                foreground="#c0392b",
            ).pack(pady=20)

        footer = ttk.Label(
            self,
            text="שלב ה' | Yuval Schmidet & Yedidya Bar-Gad | PostgreSQL + Python/Tkinter",
            style="Muted.TLabel",
        )
        footer.pack(pady=8)
