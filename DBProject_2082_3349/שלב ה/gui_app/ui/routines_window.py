"""Run Phase D functions and procedures."""
import tkinter as tk
from tkinter import messagebox, ttk

import psycopg2

from config import DB_CONFIG
from database import DatabaseError, call_procedure_refcursor, get_existing_tables
from ui.styles import BG, FONT_BODY, FONT_HEAD


class RoutinesWindow(tk.Toplevel):
    def _show_proc_error(self, exc: Exception) -> None:
        err = str(exc)
        if "does not exist" in err:
            err += "\n\nהריצו פעם אחת: python seed_database.py"
        messagebox.showerror("שגיאה", err, parent=self)

    def __init__(self, parent):
        super().__init__(parent)
        self.title("פונקציות ופרוצדורות – שלב ד'")
        self.configure(bg=BG)
        self.geometry("920x580")

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self._tab_function_habitat(nb)
        self._tab_function_vet(nb)
        self._tab_procedure_checkups(nb)
        self._tab_procedure_diet(nb)
        self._tab_trigger_demo(nb)

    def _result_tree(self, parent) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, pady=8)
        tree = ttk.Treeview(frame, show="headings")
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def _show_rows(self, tree: ttk.Treeview, rows: list[tuple], headers: list[str] | None = None):
        tree.delete(*tree.get_children())
        if not rows:
            tree["columns"] = ["msg"]
            tree.heading("msg", text="אין תוצאות")
            return
        if headers is None:
            headers = [f"col{i}" for i in range(len(rows[0]))]
        tree["columns"] = headers
        for h in headers:
            tree.heading(h, text=h)
            tree.column(h, width=130)
        for row in rows:
            tree.insert("", tk.END, values=[str(v) for v in row])

    def _tab_function_habitat(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=12)
        nb.add(tab, text="פונקציה: עלות תזונה לבית גידול")

        ttk.Label(
            tab,
            text="Get_Habitat_Diet_Cost – מחשבת סך העלות היומית של תזונה לכל החיות בבית גידול",
            wraplength=700, justify=tk.RIGHT, font=FONT_BODY,
        ).pack(anchor=tk.E)

        row = ttk.Frame(tab)
        row.pack(fill=tk.X, pady=8)
        ttk.Label(row, text="בחר בית גידול:").pack(side=tk.RIGHT, padx=8)
        self.habitat_var = tk.StringVar()
        self.habitat_cb = ttk.Combobox(row, textvariable=self.habitat_var, width=40, state="readonly")
        self.habitat_cb.pack(side=tk.RIGHT)
        self._habitat_map: dict[str, int] = {}
        tree = self._result_tree(tab)
        ttk.Button(
            tab, text="הפעל פונקציה",
            command=lambda: self._run_habitat_cost(tree),
        ).pack(pady=4)
        self._load_habitats()

    def _load_habitats(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT habitatid, habitatname FROM habitat ORDER BY habitatname")
                rows = cur.fetchall()
            conn.close()
            labels = [r[1] for r in rows]
            self._habitat_map = {r[1]: r[0] for r in rows}
            self.habitat_cb["values"] = labels
            if labels:
                self.habitat_var.set(labels[0])
        except psycopg2.Error as exc:
            messagebox.showwarning("טעינה", str(exc), parent=self)

    def _run_habitat_cost(self, tree: ttk.Treeview):
        name = self.habitat_var.get()
        if name not in self._habitat_map:
            messagebox.showwarning("קלט", "נא לבחור בית גידול", parent=self)
            return
        hid = self._habitat_map[name]
        try:
            from database import call_function
            result = call_function("SELECT get_habitat_diet_cost(%s)", (hid,))
            self._show_rows(tree, [(name, result)], ["בית גידול", "סך עלות יומית"])
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    def _tab_function_vet(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=12)
        nb.add(tab, text="פונקציה: חיות לפי וטרינר")

        ttk.Label(
            tab,
            text="Get_Animals_By_Vet_RefCursor – מחזירה רשימת חיות שטופלו על ידי וטרינר",
            wraplength=700, justify=tk.RIGHT, font=FONT_BODY,
        ).pack(anchor=tk.E)

        row = ttk.Frame(tab)
        row.pack(fill=tk.X, pady=8)
        ttk.Label(row, text="בחר וטרינר:").pack(side=tk.RIGHT, padx=8)
        self.vet_var = tk.StringVar()
        self.vet_cb = ttk.Combobox(row, textvariable=self.vet_var, width=40, state="readonly")
        self.vet_cb.pack(side=tk.RIGHT)
        self._vet_map: dict[str, int] = {}
        self.vet_status = ttk.Label(tab, text="", foreground="#c0392b", wraplength=680)
        self.vet_status.pack(anchor=tk.E, pady=4)
        tree = self._result_tree(tab)
        self.vet_run_btn = ttk.Button(
            tab, text="הפעל פונקציה", command=lambda: self._run_vet_cursor(tree),
        )
        self.vet_run_btn.pack(pady=4)
        self._load_vets()

    def _load_vets(self):
        if "veterinarian" not in get_existing_tables():
            self.vet_status.config(
                text="טבלת veterinarian לא קיימת – הריצו: python seed_database.py",
            )
            self.vet_cb["values"] = []
            self.vet_run_btn.state(["disabled"])
            return
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT vetid, firstname || ' ' || lastname FROM veterinarian ORDER BY 2"
                )
                rows = cur.fetchall()
            conn.close()
            labels = [r[1] for r in rows]
            self._vet_map = {r[1]: r[0] for r in rows}
            self.vet_cb["values"] = labels
            if labels:
                self.vet_var.set(labels[0])
                self.vet_status.config(text="")
                self.vet_run_btn.state(["!disabled"])
            else:
                self.vet_status.config(text="אין וטרינרים בטבלה – הריצו seed_database.py")
                self.vet_run_btn.state(["disabled"])
        except psycopg2.Error as exc:
            self.vet_status.config(text=str(exc))
            self.vet_run_btn.state(["disabled"])

    def _run_vet_cursor(self, tree: ttk.Treeview):
        name = self.vet_var.get()
        if name not in self._vet_map:
            return
        vid = self._vet_map[name]
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SELECT get_animals_by_vet_refcursor(%s)", (vid,))
                cursor_name = cur.fetchone()[0]
                cur.execute(f'FETCH ALL IN "{cursor_name}"')
                rows = cur.fetchall()
            conn.commit()
            conn.close()
            headers = ["מזהה חיה", "שם", "תאריך לידה", "תאריך ביקור", "סיבה"]
            self._show_rows(tree, rows, headers)
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    def _tab_procedure_checkups(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=12)
        nb.add(tab, text="פרוצדורה: בדיקות שגרה")

        ttk.Label(
            tab,
            text="Process_Routine_Checkups – יוצרת רשומות בריאות לחיות ללא בדיקה בשנה האחרונה",
            wraplength=700, justify=tk.RIGHT, font=FONT_BODY,
        ).pack(anchor=tk.E)
        tree = self._result_tree(tab)
        ttk.Button(tab, text="הפעל פרוצדורה", command=lambda: self._run_checkups(tree)).pack(pady=8)

    def _run_checkups(self, tree: ttk.Treeview):
        try:
            rows = call_procedure_refcursor("process_routine_checkups", ())
            headers = ["מזהה", "תאריך", "משקל", "סטטוס", "חיה"] if rows else None
            self._show_rows(tree, rows, headers)
            messagebox.showinfo("הושלם", f"נוצרו {len(rows)} רשומות בריאות חדשות", parent=self)
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    def _tab_procedure_diet(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=12)
        nb.add(tab, text="פרוצדורה: עדכון עלות תזונה")

        ttk.Label(
            tab,
            text="Adjust_Diet_Cost_By_Species – מעלה את עלות התזונה לפי אחוז למין נבחר",
            wraplength=700, justify=tk.RIGHT, font=FONT_BODY,
        ).pack(anchor=tk.E)

        form = ttk.Frame(tab)
        form.pack(fill=tk.X, pady=8)
        ttk.Label(form, text="מין:").grid(row=0, column=2, padx=6)
        self.species_var = tk.StringVar()
        self.species_cb = ttk.Combobox(form, textvariable=self.species_var, width=30, state="readonly")
        self.species_cb.grid(row=0, column=1)
        self._species_map: dict[str, int] = {}

        ttk.Label(form, text="אחוז העלאה:").grid(row=1, column=2, padx=6, pady=6)
        self.pct_var = tk.StringVar(value="10")
        ttk.Entry(form, textvariable=self.pct_var, width=10).grid(row=1, column=1, pady=6)

        tree = self._result_tree(tab)
        ttk.Button(tab, text="הפעל פרוצדורה", command=lambda: self._run_adjust_diet(tree)).pack(pady=4)
        self._load_species()

    def _load_species(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT speciesid, commonname FROM species ORDER BY commonname")
                rows = cur.fetchall()
            conn.close()
            labels = [r[1] for r in rows]
            self._species_map = {r[1]: r[0] for r in rows}
            self.species_cb["values"] = labels
            if labels:
                self.species_var.set(labels[0])
        except psycopg2.Error as exc:
            messagebox.showwarning("טעינה", str(exc), parent=self)

    def _run_adjust_diet(self, tree: ttk.Treeview):
        name = self.species_var.get()
        if name not in self._species_map:
            return
        try:
            pct = float(self.pct_var.get())
        except ValueError:
            messagebox.showwarning("קלט", "אחוז לא תקין", parent=self)
            return
        sid = self._species_map[name]
        try:
            rows = call_procedure_refcursor("adjust_diet_cost_by_species", (sid, pct))
            self._show_rows(tree, rows, ["מזהה תוכנית", "עלות יומית", "שם תוכנית"])
            messagebox.showinfo("הושלם", "עלויות התזונה עודכנו", parent=self)
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    def _tab_trigger_demo(self, nb: ttk.Notebook):
        tab = ttk.Frame(nb, padding=12)
        nb.add(tab, text="הדגמת Triggers")

        ttk.Label(
            tab,
            text=(
                "עדכון MaxCapacity בטבלת habitat מפעיל Trg_Habitat_Capacity_Log.\n"
                "עדכון Cost > 500 ב-medicalvisit דורש Summary (Trg_Prevent_Invalid_Medical_Cost)."
            ),
            wraplength=700, justify=tk.RIGHT, font=FONT_BODY,
        ).pack(anchor=tk.E, pady=8)

        lf = ttk.LabelFrame(tab, text="עדכון קיבולת → יומן", padding=8)
        lf.pack(fill=tk.X, pady=6)
        self.cap_habitat = tk.StringVar()
        self.cap_habitat_cb = ttk.Combobox(
            lf, textvariable=self.cap_habitat, width=35, state="readonly",
        )
        self.cap_habitat_cb.pack(side=tk.RIGHT)
        self.cap_value = tk.StringVar(value="100")
        ttk.Entry(lf, textvariable=self.cap_value, width=8).pack(side=tk.RIGHT, padx=6)
        ttk.Label(lf, text="קיבולת חדשה:").pack(side=tk.RIGHT)
        ttk.Button(lf, text="עדכן והצג יומן", command=self._demo_capacity_trigger).pack(
            side=tk.LEFT, padx=8
        )
        self._cap_habitat_map: dict[str, int] = {}
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT habitatid, habitatname FROM habitat ORDER BY 1 LIMIT 20")
                rows = cur.fetchall()
            conn.close()
            labels = [r[1] for r in rows]
            self._cap_habitat_map = {r[1]: r[0] for r in rows}
            self.cap_habitat_cb["values"] = labels
            if labels:
                self.cap_habitat.set(labels[0])
        except psycopg2.Error:
            pass

        self.trigger_log = self._result_tree(tab)

    def _demo_capacity_trigger(self):
        name = self.cap_habitat.get()
        if name not in self._cap_habitat_map:
            return
        try:
            cap = int(self.cap_value.get())
        except ValueError:
            messagebox.showwarning("קלט", "קיבולת לא תקינה", parent=self)
            return
        hid = self._cap_habitat_map[name]
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("UPDATE habitat SET maxcapacity = %s WHERE habitatid = %s", (cap, hid))
                cur.execute(
                    """SELECT h.habitatname, l.oldcapacity, l.newcapacity, l.changedate
                       FROM habitat_capacity_log l
                       JOIN habitat h ON l.habitatid = h.habitatid
                       WHERE l.habitatid = %s ORDER BY l.changedate DESC LIMIT 5""",
                    (hid,),
                )
                rows = cur.fetchall()
            conn.commit()
            conn.close()
            self._show_rows(
                self.trigger_log, rows,
                ["בית גידול", "קודם", "חדש", "תאריך"],
            )
        except psycopg2.Error as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
