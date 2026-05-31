"""Generic CRUD window – dark-mode redesign with tab panel."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from database import DatabaseError, execute, fetch_all, fetch_one, next_id
from table_metadata import TableDef, all_editable_columns, build_select_sql, pk_labels
from ui.styles import (
    ACCENT, BG, BG2, BG3, BORDER,
    DANGER, DANGER_DK, FONT_BODY, FONT_HEAD, FONT_SMALL, FONT_TITLE,
    GUTTER, PAD, PRIMARY, PRIMARY_DK, PRIMARY_LT,
    SUCCESS, TEXT, TEXT_MUTED, TEXT_DIM,
    configure_styles, tag_treeview_rows,
)

_HS_COLOR = {
    "Healthy":    SUCCESS,
    "Sick":       "#ffa502",
    "Recovering": "#74b9ff",
    "Critical":   DANGER,
    "Deceased":   "#636e72",
}


class CrudWindow(tk.Toplevel):
    def __init__(self, parent, tdef: TableDef):
        super().__init__(parent)
        self.tdef = tdef
        self.title(f"ניהול – {tdef.display_name}")
        self.configure(bg=BG)
        self.geometry("1060x660")
        self.minsize(860, 520)
        configure_styles(self)

        self._build_header()
        self._build_body()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#111e2d", height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text=self.tdef.display_name,
                 bg="#111e2d", fg=PRIMARY_LT, font=FONT_TITLE,
                 anchor="e").pack(side=tk.RIGHT, padx=PAD)

        tk.Button(hdr, text="✕  סגור", bg=BG3, fg=TEXT_MUTED,
                  font=FONT_SMALL, relief="flat", cursor="hand2",
                  command=self.destroy).pack(side=tk.LEFT, padx=PAD, pady=10, ipadx=8)

        if self.tdef.read_only:
            tk.Label(hdr,
                     text="📋 טבלת יומן – נוצרת אוטומטית על ידי Trigger",
                     bg="#111e2d", fg=ACCENT, font=FONT_SMALL).pack(side=tk.LEFT, padx=8)

    # ── Main body (Notebook) ─────────────────────────────────────────────────
    def _build_body(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 12))

        self._build_read_tab(nb)
        if not self.tdef.read_only:
            self._build_insert_tab(nb)
            self._build_update_tab(nb)
            self._build_delete_tab(nb)

    # ── READ tab ──────────────────────────────────────────────────────────────
    def _build_read_tab(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  📖  שליפה  ")

        # Toolbar
        toolbar = tk.Frame(tab, bg=BG3, height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="תוצאות:", bg=BG3, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side=tk.RIGHT, padx=PAD)
        self.count_label = tk.Label(toolbar, text="0 רשומות",
                                    bg=BG3, fg=PRIMARY_LT, font=FONT_HEAD)
        self.count_label.pack(side=tk.RIGHT, padx=4)

        _ToolBtn(toolbar, text="🔄  רענון", command=self._refresh_grid
                 ).pack(side=tk.LEFT, padx=PAD, pady=6, ipadx=8)

        self.hint_label = tk.Label(toolbar, text="", bg=BG3, fg=DANGER, font=FONT_SMALL)
        self.hint_label.pack(side=tk.LEFT, padx=8)

        # Treeview
        tv_frame = tk.Frame(tab, bg=BG)
        tv_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(tv_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tv_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tv_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tv_frame.rowconfigure(0, weight=1)
        tv_frame.columnconfigure(0, weight=1)

        self._hidden_pk_cols: list[str] = []
        self._display_headers: list[str] = []
        self._refresh_grid()

    def _refresh_grid(self):
        sql, headers = build_select_sql(self.tdef)
        self._hidden_pk_cols = [f"__pk{i}" for i in range(len(self.tdef.pk))]
        self._display_headers = headers
        all_cols = self._hidden_pk_cols + headers

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = all_cols

        for i, pk in enumerate(self.tdef.pk):
            self.tree.heading(self._hidden_pk_cols[i], text=pk)
            self.tree.column(self._hidden_pk_cols[i], width=0, stretch=False, minwidth=0)

        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=140, anchor=tk.CENTER)
        self.tree["displaycolumns"] = headers

        # Row color tags for HealthRecord
        self.tree.tag_configure("odd",      background="#1f2f44", foreground=TEXT)
        self.tree.tag_configure("even",     background="#1a2535", foreground=TEXT)
        self.tree.tag_configure("healthy",  background="#0d2b1e", foreground=SUCCESS)
        self.tree.tag_configure("sick",     background="#2b1f0d", foreground="#ffa502")
        self.tree.tag_configure("critical", background="#2b0d0d", foreground=DANGER)
        self.tree.tag_configure("deceased", background="#1f1f1f", foreground=TEXT_MUTED)

        try:
            rows = fetch_all(sql)
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
            return

        self.count_label.configure(text=f"{len(rows)} רשומות")

        if not rows:
            self.hint_label.configure(text="אין רשומות – הריצו: python seed_database.py")
        else:
            self.hint_label.configure(text="")

        for i, row in enumerate(rows):
            pk_vals   = row[: len(self.tdef.pk)]
            disp_vals = row[len(self.tdef.pk):]
            formatted = [("" if v is None else str(v)[:90]) for v in disp_vals]

            # Pick tag
            tag = "even" if i % 2 == 0 else "odd"
            if self.tdef.key == "HEALTHRECORD" and len(formatted) >= 3:
                status = formatted[2].lower()
                if "healthy" in status:
                    tag = "healthy"
                elif "critical" in status or "deceased" in status:
                    tag = "critical" if "critical" in status else "deceased"
                elif "sick" in status:
                    tag = "sick"

            self.tree.insert("", tk.END, values=list(pk_vals) + formatted, tags=(tag,))

    # ── FK helpers ────────────────────────────────────────────────────────────
    def _load_fk_options(self, fk) -> list[tuple[int, str]]:
        ref = fk.ref_table.lower()
        sql = f"SELECT {fk.ref_pk}, {fk.display_sql} AS lbl FROM {ref} ORDER BY 2"
        if ref == "activity":
            sql = ("SELECT activityid, activityid::text || ' – ' || activitydate::text "
                   "FROM activity ORDER BY activityid")
        elif ref == "medicalvisit":
            sql = ("SELECT visitid, visitid::text || ' – ' || reason "
                   "FROM medicalvisit ORDER BY visitid")
        elif ref == "veterinarian":
            sql = "SELECT vetid, firstname || ' ' || lastname FROM veterinarian ORDER BY 2"
        elif ref == "employee":
            sql = "SELECT employeeid, firstname || ' ' || lastname FROM employee ORDER BY 2"
        rows = fetch_all(sql)
        return [(int(r[0]), str(r[1])) for r in rows]

    # ── Form builder ─────────────────────────────────────────────────────────
    def _make_form(self, parent, include_pk: bool = False) -> dict[str, tk.Variable]:
        outer = tk.Frame(parent, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=PAD)

        canvas = tk.Canvas(outer, bg=BG2, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        form_inner = tk.Frame(canvas, bg=BG2)

        win = canvas.create_window((0, 0), window=form_inner, anchor="nw")
        form_inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        vars_map: dict[str, tk.Variable] = {}
        row = 0

        def _add_field(label_text, widget_factory):
            nonlocal row
            # Right-side label
            tk.Label(form_inner, text=label_text,
                     bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL,
                     anchor="e").grid(row=row, column=1, sticky="e",
                                      padx=(PAD, 6), pady=(8, 0))
            # Left-side widget
            widget_factory(form_inner, row)
            row += 1

        form_inner.columnconfigure(0, weight=1)

        if include_pk:
            for pk, lbl in zip(self.tdef.pk, pk_labels(self.tdef)):
                var = tk.StringVar()
                vars_map[pk] = var

                def _make_pk(p, v):
                    def factory(parent, r):
                        e = ttk.Entry(parent, textvariable=v, width=20)
                        e.grid(row=r, column=0, sticky="w", padx=PAD, pady=(8, 0))
                    return factory

                _add_field(lbl, _make_pk(pk, var))

        for col in all_editable_columns(self.tdef):
            if col.field_type == "readonly":
                continue

            if col.field_type == "fk":
                fk = next(f for f in self.tdef.foreign_keys if f.column == col.name)
                var = tk.StringVar()
                vars_map[col.name] = var

                def _make_fk(fk_ref, v):
                    def factory(parent, r):
                        cb = ttk.Combobox(parent, textvariable=v, width=38, state="readonly")
                        try:
                            opts = self._load_fk_options(fk_ref)
                            cb["values"] = [lbl for _, lbl in opts]
                            cb._id_map = {lbl: id_ for id_, lbl in opts}  # type: ignore
                        except DatabaseError:
                            cb["values"] = []
                            cb._id_map = {}  # type: ignore
                        cb.grid(row=r, column=0, sticky="w", padx=PAD, pady=(8, 0))
                    return factory

                _add_field(col.label, _make_fk(fk, var))

            elif col.choices:
                var = tk.StringVar()
                vars_map[col.name] = var

                def _make_choice(choices, v):
                    def factory(parent, r):
                        cb = ttk.Combobox(parent, textvariable=v, values=choices,
                                          width=28, state="readonly")
                        cb.grid(row=r, column=0, sticky="w", padx=PAD, pady=(8, 0))
                    return factory

                _add_field(col.label, _make_choice(col.choices, var))

            else:
                var = tk.StringVar()
                vars_map[col.name] = var

                def _make_entry(v):
                    def factory(parent, r):
                        e = ttk.Entry(parent, textvariable=v, width=36)
                        e.grid(row=r, column=0, sticky="w", padx=PAD, pady=(8, 0))
                    return factory

                _add_field(col.label, _make_entry(var))

        # Bottom padding
        tk.Frame(form_inner, bg=BG2, height=PAD).grid(row=row, column=0)
        return vars_map

    # ── Collect form values ───────────────────────────────────────────────────
    def _collect_values(self, vars_map: dict, form_frame=None) -> dict:
        data = {}
        for col in all_editable_columns(self.tdef):
            if col.field_type == "readonly":
                continue
            if col.field_type == "fk":
                fk = next(f for f in self.tdef.foreign_keys if f.column == col.name)
                lbl = vars_map[col.name].get()
                opts = self._load_fk_options(fk)
                id_map = {l: i for i, l in opts}
                if lbl not in id_map:
                    raise ValueError(f"נא לבחור {col.label}")
                data[col.name] = id_map[lbl]
            else:
                val = vars_map[col.name].get().strip()
                if not val and col.field_type != "text":
                    raise ValueError(f"שדה חובה: {col.label}")
                if col.field_type == "int":
                    data[col.name] = int(val)
                elif col.field_type == "float":
                    data[col.name] = float(val)
                else:
                    data[col.name] = val
        return data

    # ── INSERT tab ────────────────────────────────────────────────────────────
    def _build_insert_tab(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  ➕  הוספה  ")

        tk.Label(tab, text="הוספת רשומה חדשה",
                 bg=BG, fg=TEXT_MUTED, font=FONT_SMALL,
                 anchor="e").pack(fill=tk.X, padx=PAD, pady=(PAD, 0))

        self.insert_vars = self._make_form(tab)

        _ActionBtn(tab, text="➕  הוסף רשומה", color=PRIMARY,
                   command=self._insert).pack(pady=PAD, ipadx=16, ipady=6)

    def _insert(self):
        try:
            data = self._collect_values(self.insert_vars)
        except (ValueError, DatabaseError) as exc:
            _toast(self, str(exc), kind="warn")
            return

        if len(self.tdef.pk) == 1:
            pk = self.tdef.pk[0]
            if pk not in data and pk != "logid":
                data[pk] = next_id(self.tdef.table, pk)
        else:
            for pk in self.tdef.pk:
                if pk not in data:
                    _toast(self, f"נא לבחור/להזין {pk}", kind="warn")
                    return

        cols = list(data.keys())
        vals = list(data.values())
        sql = (f"INSERT INTO {self.tdef.table} ({', '.join(cols)}) "
               f"VALUES ({', '.join(['%s'] * len(vals))})")
        try:
            execute(sql, tuple(vals))
            _toast(self, "✅ הרשומה נוספה בהצלחה", kind="ok")
            self._refresh_grid()
        except DatabaseError as exc:
            _toast(self, str(exc), kind="error")

    # ── UPDATE tab ────────────────────────────────────────────────────────────
    def _build_update_tab(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  ✏️  עדכון  ")

        key_card = tk.Frame(tab, bg=BG3, highlightbackground=BORDER, highlightthickness=1)
        key_card.pack(fill=tk.X, padx=PAD, pady=(PAD, 0))

        tk.Label(key_card, text="🔍  הזן מפתח לטעינת רשומה",
                 bg=BG3, fg=ACCENT, font=FONT_HEAD).pack(anchor="e", padx=PAD, pady=(8, 4))

        self.update_key_vars: dict[str, tk.StringVar] = {}
        row_f = tk.Frame(key_card, bg=BG3)
        row_f.pack(fill=tk.X, padx=PAD, pady=(0, 8))

        for i, (pk, lbl) in enumerate(zip(self.tdef.pk, pk_labels(self.tdef))):
            tk.Label(row_f, text=lbl, bg=BG3, fg=TEXT_MUTED,
                     font=FONT_SMALL).grid(row=0, column=i * 2 + 1, padx=6)
            var = tk.StringVar()
            self.update_key_vars[pk] = var
            ttk.Entry(row_f, textvariable=var, width=14).grid(row=0, column=i * 2, padx=4)

        _ToolBtn(row_f, text="📂  טען רשומה",
                 command=self._load_for_update).grid(
            row=0, column=len(self.tdef.pk) * 2, padx=PAD)

        self.update_vars = self._make_form(tab)

        _ActionBtn(tab, text="💾  שמור עדכון", color="#1e90ff",
                   command=self._update).pack(pady=PAD, ipadx=16, ipady=6)

    def _load_for_update(self):
        conditions, params = [], []
        for pk in self.tdef.pk:
            val = self.update_key_vars[pk].get().strip()
            if not val:
                _toast(self, "נא למלא את כל שדות המפתח", kind="warn")
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val) if pk.endswith("id") else val)

        sel = ", ".join([c.name for c in self.tdef.columns] +
                        [f.column for f in self.tdef.foreign_keys])
        try:
            row = fetch_one(
                f"SELECT {sel} FROM {self.tdef.table} WHERE {' AND '.join(conditions)}",
                tuple(params),
            )
        except DatabaseError as exc:
            _toast(self, str(exc), kind="error")
            return
        if not row:
            _toast(self, "לא נמצאה רשומה עם המפתח שהוזן", kind="warn")
            return

        idx = 0
        for col in self.tdef.columns:
            if col.name in self.update_vars:
                v = row[idx]
                self.update_vars[col.name].set("" if v is None else str(v))
            idx += 1
        for fk in self.tdef.foreign_keys:
            fk_id = row[idx]
            idx += 1
            try:
                opts = self._load_fk_options(fk)
                label = next((l for i, l in opts if i == int(fk_id)), "")
                if fk.column in self.update_vars:
                    self.update_vars[fk.column].set(label)
            except (ValueError, TypeError):
                pass

    def _update(self):
        conditions, params = [], []
        for pk in self.tdef.pk:
            val = self.update_key_vars[pk].get().strip()
            if not val:
                _toast(self, "נא למלא מפתח לפני עדכון", kind="warn")
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val))

        try:
            data = self._collect_values(self.update_vars)
        except (ValueError, DatabaseError) as exc:
            _toast(self, str(exc), kind="warn")
            return

        set_parts = [f"{k} = %s" for k in data]
        vals = list(data.values()) + params
        sql = (f"UPDATE {self.tdef.table} SET {', '.join(set_parts)} "
               f"WHERE {' AND '.join(conditions)}")
        try:
            n = execute(sql, tuple(vals))
            if n:
                _toast(self, "✅ הרשומה עודכנה", kind="ok")
                self._refresh_grid()
            else:
                _toast(self, "לא עודכנה אף רשומה", kind="warn")
        except DatabaseError as exc:
            _toast(self, str(exc), kind="error")

    # ── DELETE tab ────────────────────────────────────────────────────────────
    def _build_delete_tab(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  🗑️  מחיקה  ")

        card = tk.Frame(tab, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        card.pack(padx=PAD * 3, pady=PAD * 3)

        tk.Label(card, text="🗑️  מחיקת רשומה",
                 bg=BG2, fg=DANGER, font=FONT_TITLE).pack(padx=PAD * 2, pady=(PAD, 4))
        tk.Label(card,
                 text="הזינו את המפתח הראשי של הרשומה למחיקה.\nפעולה זו אינה ניתנת לביטול.",
                 bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL, justify="right").pack(padx=PAD * 2,
                                                                                pady=(0, PAD))

        self.delete_key_vars: dict[str, tk.StringVar] = {}
        for pk, lbl in zip(self.tdef.pk, pk_labels(self.tdef)):
            row_f = tk.Frame(card, bg=BG2)
            row_f.pack(padx=PAD * 2, pady=4)
            tk.Label(row_f, text=lbl, bg=BG2, fg=TEXT_MUTED,
                     font=FONT_SMALL).pack(side=tk.RIGHT, padx=6)
            var = tk.StringVar()
            self.delete_key_vars[pk] = var
            ttk.Entry(row_f, textvariable=var, width=20).pack(side=tk.RIGHT)

        _ActionBtn(card, text="🗑️  מחק רשומה", color=DANGER,
                   command=self._delete).pack(pady=PAD * 2, ipadx=20, ipady=8)

    def _delete(self):
        if not messagebox.askyesno(
            "אישור מחיקה",
            "האם למחוק את הרשומה? פעולה זו אינה ניתנת לביטול.",
            parent=self,
        ):
            return
        conditions, params = [], []
        for pk in self.tdef.pk:
            val = self.delete_key_vars[pk].get().strip()
            if not val:
                _toast(self, "נא למלא את כל שדות המפתח", kind="warn")
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val))
        sql = f"DELETE FROM {self.tdef.table} WHERE {' AND '.join(conditions)}"
        try:
            n = execute(sql, tuple(params))
            if n:
                _toast(self, "✅ הרשומה נמחקה", kind="ok")
                self._refresh_grid()
            else:
                _toast(self, "לא נמצאה רשומה למחיקה", kind="warn")
        except DatabaseError as exc:
            _toast(self, str(exc), kind="error")


# ── Shared helper widgets ─────────────────────────────────────────────────────

class _ToolBtn(tk.Label):
    """Small toolbar button."""
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent, text=text, bg=BG3, fg=TEXT_MUTED,
                         font=FONT_SMALL, cursor="hand2", padx=8, pady=4,
                         relief="flat", **kw)
        self.bind("<Enter>", lambda _: self.configure(bg=BG2, fg=TEXT))
        self.bind("<Leave>", lambda _: self.configure(bg=BG3, fg=TEXT_MUTED))
        self.bind("<Button-1>", lambda _: command())


class _ActionBtn(tk.Label):
    """Large action button with color."""
    def __init__(self, parent, text, color, command, **kw):
        super().__init__(parent, text=text, bg=color, fg="white",
                         font=FONT_HEAD, cursor="hand2", relief="flat", **kw)
        darker = _darken(color)
        self.bind("<Enter>", lambda _: self.configure(bg=darker))
        self.bind("<Leave>", lambda _: self.configure(bg=color))
        self.bind("<Button-1>", lambda _: command())


def _darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def _toast(parent, message: str, kind: str = "ok"):
    """Show a small auto-dismissing toast overlay on the window."""
    colors = {"ok": SUCCESS, "warn": "#ffa502", "error": DANGER}
    bg = colors.get(kind, SUCCESS)
    toast = tk.Toplevel(parent)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)

    # Position at top-center of parent
    parent.update_idletasks()
    pw = parent.winfo_width()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    tw = min(500, pw - 40)
    tx = px + (pw - tw) // 2
    ty = py + 56

    toast.geometry(f"{tw}x40+{tx}+{ty}")
    toast.configure(bg=bg)
    tk.Label(toast, text=message, bg=bg, fg="white",
             font=FONT_SMALL, wraplength=tw - 20).pack(fill=tk.BOTH, expand=True, padx=8)

    toast.after(2200, toast.destroy)
