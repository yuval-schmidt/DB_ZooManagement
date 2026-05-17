"""Generic CRUD window for a single table."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from database import DatabaseError, execute, fetch_all, fetch_one, next_id
from table_metadata import TableDef, all_editable_columns, build_select_sql, pk_labels
from ui.styles import BG, CARD, DANGER, FONT_BODY, FONT_HEAD, PRIMARY


class CrudWindow(tk.Toplevel):
    def __init__(self, parent, tdef: TableDef):
        super().__init__(parent)
        self.tdef = tdef
        self.title(f"ניהול – {tdef.display_name}")
        self.configure(bg=BG)
        self.geometry("960x620")
        self.minsize(800, 500)

        header = ttk.Frame(self, padding=(16, 12))
        header.pack(fill=tk.X)
        ttk.Label(header, text=tdef.display_name, style="Title.TLabel").pack(side=tk.RIGHT)
        ttk.Button(header, text="סגור", command=self.destroy).pack(side=tk.LEFT)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._build_read_tab(nb)
        if not tdef.read_only:
            self._build_insert_tab(nb)
            self._build_update_tab(nb)
            self._build_delete_tab(nb)
        else:
            ttk.Label(
                self,
                text="טבלת יומן – נוצרת אוטומטית על ידי Trigger בעדכון קיבולת בית גידול",
                style="Muted.TLabel",
            ).pack(pady=4)

    def _build_read_tab(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="שליפה (Read)")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        self.empty_hint = ttk.Label(toolbar, text="", foreground="#c0392b")
        self.empty_hint.pack(side=tk.RIGHT, padx=8)
        ttk.Button(toolbar, text="רענון", command=self._refresh_grid).pack(side=tk.RIGHT)

        cols_frame = ttk.Frame(tab)
        cols_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(cols_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(cols_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(cols_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        cols_frame.rowconfigure(0, weight=1)
        cols_frame.columnconfigure(0, weight=1)

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
        for h, col_id in zip(headers, headers):
            self.tree.heading(col_id, text=h)
            self.tree.column(col_id, width=120, anchor=tk.CENTER)
        self.tree["displaycolumns"] = headers

        try:
            rows = fetch_all(sql)
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
            return

        self.title(f"ניהול – {self.tdef.display_name} ({len(rows)} רשומות)")

        if not rows:
            self.empty_hint.config(
                text="אין רשומות – הריצו: python seed_database.py",
            )
        else:
            self.empty_hint.config(text="")

        for row in rows:
            pk_vals = row[: len(self.tdef.pk)]
            display_vals = row[len(self.tdef.pk) :]
            formatted = []
            for v in display_vals:
                formatted.append("" if v is None else str(v)[:80])
            self.tree.insert("", tk.END, values=list(pk_vals) + formatted)

    def _load_fk_options(self, fk) -> list[tuple[int, str]]:
        ref = fk.ref_table.lower()
        sql = f"SELECT {fk.ref_pk}, {fk.display_sql} AS lbl FROM {ref} ORDER BY 2"
        if ref == "activity":
            sql = (
                f"SELECT activityid, activityid::text || ' – ' || activitydate::text "
                f"FROM activity ORDER BY activityid"
            )
        elif ref == "medicalvisit":
            sql = (
                "SELECT visitid, visitid::text || ' – ' || reason "
                "FROM medicalvisit ORDER BY visitid"
            )
        elif ref == "veterinarian":
            sql = (
                "SELECT vetid, firstname || ' ' || lastname FROM veterinarian ORDER BY 2"
            )
        elif ref == "employee":
            sql = (
                "SELECT employeeid, firstname || ' ' || lastname FROM employee ORDER BY 2"
            )
        rows = fetch_all(sql)
        return [(int(r[0]), str(r[1])) for r in rows]

    def _make_form(self, parent, include_pk: bool = False) -> dict[str, tk.Variable]:
        widgets_frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        widgets_frame.pack(fill=tk.BOTH, expand=True)
        vars_map: dict[str, tk.Variable] = {}
        row = 0

        if include_pk:
            for pk, lbl in zip(self.tdef.pk, pk_labels(self.tdef)):
                ttk.Label(widgets_frame, text=lbl, style="Card.TLabel").grid(
                    row=row, column=1, sticky="e", padx=8, pady=4
                )
                var = tk.StringVar()
                vars_map[pk] = var
                ttk.Entry(widgets_frame, textvariable=var, width=30).grid(
                    row=row, column=0, sticky="w", pady=4
                )
                row += 1

        for col in all_editable_columns(self.tdef):
            if col.field_type == "readonly":
                continue
            ttk.Label(widgets_frame, text=col.label, style="Card.TLabel").grid(
                row=row, column=1, sticky="e", padx=8, pady=4
            )
            if col.field_type == "fk":
                fk = next(f for f in self.tdef.foreign_keys if f.column == col.name)
                var = tk.StringVar()
                vars_map[col.name] = var
                cb = ttk.Combobox(widgets_frame, textvariable=var, width=40, state="readonly")
                try:
                    opts = self._load_fk_options(fk)
                    cb["values"] = [lbl for _, lbl in opts]
                    cb._id_map = {lbl: id_ for id_, lbl in opts}  # type: ignore[attr-defined]
                except DatabaseError:
                    cb["values"] = []
                    cb._id_map = {}  # type: ignore[attr-defined]
                cb.grid(row=row, column=0, sticky="w", pady=4)
            elif col.choices:
                var = tk.StringVar()
                vars_map[col.name] = var
                ttk.Combobox(
                    widgets_frame, textvariable=var, values=col.choices, width=28, state="readonly"
                ).grid(row=row, column=0, sticky="w", pady=4)
            else:
                var = tk.StringVar()
                vars_map[col.name] = var
                ttk.Entry(widgets_frame, textvariable=var, width=32).grid(
                    row=row, column=0, sticky="w", pady=4
                )
            row += 1
        return vars_map

    def _resolve_fk_id(self, parent_widget, column: str) -> int | None:
        for child in parent_widget.winfo_children():
            if isinstance(child, ttk.Combobox):
                lbl = child.get()
                id_map = getattr(child, "_id_map", {})
                if column in [f.column for f in self.tdef.foreign_keys]:
                    fk = next(f for f in self.tdef.foreign_keys if f.column == column)
                    if lbl in id_map:
                        return id_map[lbl]
        return None

    def _collect_values(self, vars_map: dict, form_frame: ttk.Frame) -> dict:
        data = {}
        for col in all_editable_columns(self.tdef):
            if col.field_type == "readonly":
                continue
            if col.field_type == "fk":
                for child in form_frame.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        pass
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

    def _build_insert_tab(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="הוספה (Create)")

        form = ttk.Frame(tab)
        form.pack(fill=tk.BOTH, expand=True)
        self.insert_vars = self._make_form(form)
        self.insert_form_frame = form.winfo_children()[0] if form.winfo_children() else form

        ttk.Button(tab, text="הוסף רשומה", style="Primary.TButton", command=self._insert).pack(
            pady=8
        )

    def _insert(self):
        form_frame = self.insert_form_frame
        try:
            data = self._collect_values(self.insert_vars, form_frame)
        except (ValueError, DatabaseError) as exc:
            messagebox.showwarning("קלט", str(exc), parent=self)
            return

        if len(self.tdef.pk) == 1:
            pk = self.tdef.pk[0]
            if pk not in data and pk != "logid":
                data[pk] = next_id(self.tdef.table, pk)
        else:
            for pk in self.tdef.pk:
                if pk not in data:
                    messagebox.showwarning("קלט", f"נא לבחור/להזין {pk}", parent=self)
                    return

        cols = list(data.keys())
        vals = list(data.values())
        sql = (
            f"INSERT INTO {self.tdef.table} ({', '.join(cols)}) "
            f"VALUES ({', '.join(['%s'] * len(vals))})"
        )

        try:
            execute(sql, tuple(vals))
            messagebox.showinfo("הצלחה", "הרשומה נוספה בהצלחה", parent=self)
            self._refresh_grid()
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)

    def _build_update_tab(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="עדכון (Update)")

        key_frame = ttk.LabelFrame(tab, text="הזנת מפתח לטעינה", padding=8)
        key_frame.pack(fill=tk.X, pady=(0, 8))
        self.update_key_vars: dict[str, tk.StringVar] = {}
        for i, (pk, lbl) in enumerate(zip(self.tdef.pk, pk_labels(self.tdef))):
            ttk.Label(key_frame, text=lbl).grid(row=0, column=i * 2 + 1, padx=4)
            var = tk.StringVar()
            self.update_key_vars[pk] = var
            ttk.Entry(key_frame, textvariable=var, width=14).grid(row=0, column=i * 2, padx=4)
        ttk.Button(key_frame, text="טען רשומה", command=self._load_for_update).grid(
            row=0, column=len(self.tdef.pk) * 2, padx=8
        )

        self.update_form = ttk.Frame(tab)
        self.update_form.pack(fill=tk.BOTH, expand=True)
        self.update_vars = self._make_form(self.update_form)
        self.update_form_frame = self.update_form.winfo_children()[0]

        ttk.Button(tab, text="שמור עדכון", style="Primary.TButton", command=self._update).pack(
            pady=8
        )

    def _load_for_update(self):
        conditions = []
        params = []
        for pk in self.tdef.pk:
            val = self.update_key_vars[pk].get().strip()
            if not val:
                messagebox.showwarning("קלט", "נא למלא את כל שדות המפתח", parent=self)
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val) if pk.endswith("id") else val)

        sql = f"SELECT * FROM {self.tdef.table} WHERE {' AND '.join(conditions)}"
        try:
            row = fetch_one(sql, tuple(params))
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
            return
        if not row:
            messagebox.showinfo("לא נמצא", "לא נמצאה רשומה עם המפתח שהוזן", parent=self)
            return

        col_names = [c.name for c in self.tdef.columns] + [f.column for f in self.tdef.foreign_keys]
        # SELECT * order matches table definition in PostgreSQL - use information approach
        with_cols = all_editable_columns(self.tdef)
        # Re-fetch with explicit columns
        sel = ", ".join([c.name for c in self.tdef.columns] + [f.column for f in self.tdef.foreign_keys])
        row = fetch_one(f"SELECT {sel} FROM {self.tdef.table} WHERE {' AND '.join(conditions)}", tuple(params))
        if not row:
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
            opts = self._load_fk_options(fk)
            label = next((l for i, l in opts if i == int(fk_id)), "")
            if fk.column in self.update_vars:
                self.update_vars[fk.column].set(label)

    def _update(self):
        conditions = []
        params = []
        for pk in self.tdef.pk:
            val = self.update_key_vars[pk].get().strip()
            if not val:
                messagebox.showwarning("קלט", "נא למלא מפתח לפני עדכון", parent=self)
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val))

        try:
            data = self._collect_values(self.update_vars, self.update_form_frame)
        except (ValueError, DatabaseError) as exc:
            messagebox.showwarning("קלט", str(exc), parent=self)
            return

        set_parts = [f"{k} = %s" for k in data]
        vals = list(data.values()) + params
        sql = f"UPDATE {self.tdef.table} SET {', '.join(set_parts)} WHERE {' AND '.join(conditions)}"
        try:
            n = execute(sql, tuple(vals))
            if n:
                messagebox.showinfo("הצלחה", "הרשומה עודכנה", parent=self)
                self._refresh_grid()
            else:
                messagebox.showwarning("עדכון", "לא עודכנה אף רשומה", parent=self)
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)

    def _build_delete_tab(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="מחיקה (Delete)")

        frame = ttk.Frame(tab, padding=12)
        frame.pack(fill=tk.X)
        self.delete_key_vars: dict[str, tk.StringVar] = {}
        for i, (pk, lbl) in enumerate(zip(self.tdef.pk, pk_labels(self.tdef))):
            ttk.Label(frame, text=lbl).grid(row=i, column=1, sticky="e", padx=8, pady=6)
            var = tk.StringVar()
            self.delete_key_vars[pk] = var
            ttk.Entry(frame, textvariable=var, width=20).grid(row=i, column=0, pady=6)

        ttk.Button(
            frame, text="מחק רשומה", command=self._delete,
        ).grid(row=len(self.tdef.pk), column=0, columnspan=2, pady=12)

    def _delete(self):
        if not messagebox.askyesno("אישור", "האם למחוק את הרשומה?", parent=self):
            return
        conditions = []
        params = []
        for pk in self.tdef.pk:
            val = self.delete_key_vars[pk].get().strip()
            if not val:
                messagebox.showwarning("קלט", "נא למלא את כל שדות המפתח", parent=self)
                return
            conditions.append(f"{pk} = %s")
            params.append(int(val))
        sql = f"DELETE FROM {self.tdef.table} WHERE {' AND '.join(conditions)}"
        try:
            n = execute(sql, tuple(params))
            if n:
                messagebox.showinfo("הצלחה", "הרשומה נמחקה", parent=self)
                self._refresh_grid()
            else:
                messagebox.showinfo("מחיקה", "לא נמצאה רשומה למחיקה", parent=self)
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
