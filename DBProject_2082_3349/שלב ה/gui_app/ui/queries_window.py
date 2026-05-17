"""Run Phase B analytical queries."""
import tkinter as tk
from tkinter import messagebox, ttk

from database import DatabaseError, fetch_all
from queries_data import PHASE_B_QUERIES
from ui.styles import BG, FONT_BODY, FONT_HEAD


class QueriesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("שאילתות – שלב ב'")
        self.configure(bg=BG)
        self.geometry("900x560")

        left = ttk.Frame(self, padding=12)
        left.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(left, text="בחר שאילתה", font=FONT_HEAD).pack(anchor=tk.E, pady=(0, 8))

        self.query_keys = list(PHASE_B_QUERIES.keys())
        self.listbox = tk.Listbox(
            left, width=36, height=12, font=FONT_BODY,
            selectbackground="#1a5f4a", selectforeground="white",
        )
        for key in self.query_keys:
            self.listbox.insert(tk.END, PHASE_B_QUERIES[key]["title"])
        self.listbox.pack(fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        ttk.Button(left, text="הרץ שאילתה", command=self._run).pack(pady=8, fill=tk.X)

        right = ttk.Frame(self, padding=12)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.desc = ttk.Label(right, text="", wraplength=520, justify=tk.RIGHT)
        self.desc.pack(anchor=tk.E, pady=(0, 8))

        tree_frame = ttk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        if self.query_keys:
            self.listbox.selection_set(0)
            self._on_select()

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        q = PHASE_B_QUERIES[self.query_keys[sel[0]]]
        self.desc.config(text=q["description"])

    def _run(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        q = PHASE_B_QUERIES[self.query_keys[sel[0]]]
        try:
            rows = fetch_all(q["sql"])
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
            return

        self.tree.delete(*self.tree.get_children())
        if not rows:
            self.tree["columns"] = ["msg"]
            self.tree.heading("msg", text="הודעה")
            self.tree.column("msg", width=400)
            self.tree.insert("", tk.END, values=(
                "אין תוצאות – ייתכן שאין נתונים בטבלאות או שבחרתם בסיס נתונים ריק (השתמשו ב-zoo_db)",
            ))
            return

        ncols = len(rows[0])
        cols = [f"c{i}" for i in range(ncols)]
        self.tree["columns"] = cols
        for i, c in enumerate(cols):
            self.tree.heading(c, text=f"עמודה {i + 1}")
            self.tree.column(c, width=140)
        for row in rows:
            self.tree.insert("", tk.END, values=[str(v) for v in row])
