"""Phase D functions, procedures and trigger demo – dark mode redesign."""
import tkinter as tk
from tkinter import messagebox, ttk

import psycopg2

from config import DB_CONFIG
from database import DatabaseError, call_function, call_procedure_refcursor, fetch_all, get_existing_tables
from ui.styles import (
    ACCENT, ACCENT_LT, BG, BG2, BG3, BORDER,
    DANGER, FONT_BODY, FONT_HEAD, FONT_SMALL, FONT_TITLE,
    PAD, PRIMARY, PRIMARY_LT,
    SUCCESS, TEXT, TEXT_DIM, TEXT_MUTED,
    configure_styles,
)

# ── Colour scheme per routine type ────────────────────────────────────────────
_FUNC_COLOR  = PRIMARY        # teal-green for functions
_PROC_COLOR  = "#a29bfe"      # soft purple for procedures
_TRIG_COLOR  = ACCENT         # gold for trigger demo


def _animal_name_map(animal_ids: list[int]) -> dict[int, str]:
    if not animal_ids:
        return {}
    rows = fetch_all(
        "SELECT animalid, name FROM animal WHERE animalid = ANY(%s)",
        (list(set(animal_ids)),),
    )
    return {int(r[0]): str(r[1]) for r in rows}


class RoutinesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ פונקציות ופרוצדורות – שלב ד'")
        self.configure(bg=BG)
        self.geometry("1040x660")
        self.minsize(820, 520)
        configure_styles(self)

        self._build_header()

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 12))

        self._tab_function_habitat(nb)
        self._tab_function_vet(nb)
        self._tab_procedure_checkups(nb)
        self._tab_procedure_diet(nb)
        self._tab_trigger_demo(nb)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#111e2d", height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙️  פונקציות ופרוצדורות – שלב ד'",
                 bg="#111e2d", fg=PRIMARY_LT, font=FONT_TITLE,
                 anchor="e").pack(side=tk.RIGHT, padx=PAD)
        tk.Button(hdr, text="✕  סגור", bg=BG3, fg=TEXT_MUTED,
                  font=FONT_SMALL, relief="flat", cursor="hand2",
                  command=self.destroy).pack(side=tk.LEFT, padx=PAD, pady=10, ipadx=8)

    # ── Shared helpers ────────────────────────────────────────────────────────
    def _result_tree(self, parent) -> ttk.Treeview:
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, pady=8)
        tree = ttk.Treeview(frame, show="headings")
        vsb  = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def _show_rows(self, tree: ttk.Treeview, rows: list[tuple],
                   headers: list[str] | None = None,
                   row_color: str = "#1f2f44"):
        tree.delete(*tree.get_children())
        if not rows:
            tree["columns"] = ["msg"]
            tree.heading("msg", text="אין תוצאות")
            tree.column("msg", width=400)
            return
        if headers is None:
            headers = [f"col{i}" for i in range(len(rows[0]))]
        tree["columns"] = headers
        for h in headers:
            tree.heading(h, text=h)
            tree.column(h, width=140, anchor=tk.CENTER)
        tree.tag_configure("odd",  background=row_color)
        tree.tag_configure("even", background=BG2)
        for i, row in enumerate(rows):
            tree.insert("", tk.END, values=[str(v) for v in row],
                        tags=("even" if i % 2 == 0 else "odd",))

    def _show_proc_error(self, exc: Exception):
        err = str(exc)
        if "does not exist" in err:
            err += "\n\nהריצו פעם אחת: python seed_database.py"
        messagebox.showerror("שגיאה", err, parent=self)

    # ── Routine section card ──────────────────────────────────────────────────
    def _section_card(self, parent, title: str, desc: str,
                      accent: str) -> tk.Frame:
        """Returns a styled card frame for a routine section."""
        outer = tk.Frame(parent, bg=BG2, highlightbackground=accent, highlightthickness=2)
        outer.pack(fill=tk.X, padx=4, pady=(0, 8))

        stripe = tk.Frame(outer, bg=accent, height=4)
        stripe.pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG2)
        hdr.pack(fill=tk.X, padx=PAD, pady=(8, 0))

        tk.Label(hdr, text=title, bg=BG2, fg=accent, font=FONT_HEAD,
                 anchor="e").pack(anchor="e")
        tk.Label(outer, text=desc, bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL,
                 wraplength=700, justify="right", anchor="e").pack(
            anchor="e", padx=PAD, pady=(2, 8))

        return outer

    def _run_button(self, parent, text: str, command, color: str) -> tk.Label:
        btn = tk.Label(parent, text=text, bg=color, fg="white",
                       font=FONT_HEAD, cursor="hand2", relief="flat",
                       padx=16, pady=7)
        darker = _darken(color)
        btn.bind("<Enter>", lambda _: btn.configure(bg=darker))
        btn.bind("<Leave>", lambda _: btn.configure(bg=color))
        btn.bind("<Button-1>", lambda _: command())
        return btn

    # ── Tab 1: Function – Habitat Diet Cost ───────────────────────────────────
    def _tab_function_habitat(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  🌿  עלות תזונה לבית גידול  ")

        self._section_card(
            tab,
            title="🔢 Get_Habitat_Diet_Cost",
            desc="מחשבת סך העלות היומית של תזונה לכל החיות בבית גידול נבחר.",
            accent=_FUNC_COLOR,
        )

        row_f = tk.Frame(tab, bg=BG)
        row_f.pack(fill=tk.X, padx=PAD, pady=4)
        tk.Label(row_f, text="בית גידול:", bg=BG, fg=TEXT_MUTED, font=FONT_SMALL
                 ).pack(side=tk.RIGHT, padx=6)

        self.habitat_var = tk.StringVar()
        self.habitat_cb = ttk.Combobox(row_f, textvariable=self.habitat_var,
                                        width=36, state="readonly")
        self.habitat_cb.pack(side=tk.RIGHT)
        self._habitat_map: dict[str, int] = {}

        tree = self._result_tree(tab)
        self._run_button(tab, "▶  הפעל פונקציה",
                         command=lambda: self._run_habitat_cost(tree),
                         color=_FUNC_COLOR).pack(pady=4, ipadx=0, ipady=0)

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
            result = call_function("SELECT get_habitat_diet_cost(%s)", (hid,))
            cost = f"₪ {float(result or 0):.2f}"
            self._show_rows(tree, [(name, cost)],
                            ["בית גידול", "סך עלות יומית"],
                            row_color="#0d2b1e")
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    # ── Tab 2: Function – Animals by Vet ─────────────────────────────────────
    def _tab_function_vet(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  🩺  חיות לפי וטרינר  ")

        self._section_card(
            tab,
            title="🔢 Get_Animals_By_Vet_RefCursor",
            desc="מחזירה רשימת חיות שטופלו על ידי וטרינר נבחר.",
            accent=_FUNC_COLOR,
        )

        row_f = tk.Frame(tab, bg=BG)
        row_f.pack(fill=tk.X, padx=PAD, pady=4)
        tk.Label(row_f, text="וטרינר:", bg=BG, fg=TEXT_MUTED, font=FONT_SMALL
                 ).pack(side=tk.RIGHT, padx=6)

        self.vet_var = tk.StringVar()
        self.vet_cb = ttk.Combobox(row_f, textvariable=self.vet_var,
                                    width=36, state="readonly")
        self.vet_cb.pack(side=tk.RIGHT)
        self._vet_map: dict[str, int] = {}

        self.vet_status = tk.Label(tab, text="", bg=BG, fg=DANGER,
                                    font=FONT_SMALL, anchor="e", wraplength=680)
        self.vet_status.pack(anchor="e", padx=PAD, pady=2)

        tree = self._result_tree(tab)
        self.vet_run_btn = self._run_button(
            tab, "▶  הפעל פונקציה",
            command=lambda: self._run_vet_cursor(tree),
            color=_FUNC_COLOR,
        )
        self.vet_run_btn.pack(pady=4)
        self._load_vets()

    def _load_vets(self):
        if "veterinarian" not in get_existing_tables():
            self.vet_status.configure(text="טבלת veterinarian לא קיימת")
            self.vet_cb["values"] = []
            return
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT vetid, firstname || ' ' || lastname "
                            "FROM veterinarian ORDER BY 2")
                rows = cur.fetchall()
            conn.close()
            labels = [r[1] for r in rows]
            self._vet_map = {r[1]: r[0] for r in rows}
            self.vet_cb["values"] = labels
            if labels:
                self.vet_var.set(labels[0])
                self.vet_status.configure(text="")
            else:
                self.vet_status.configure(text="אין וטרינרים – הריצו seed_database.py")
        except psycopg2.Error as exc:
            self.vet_status.configure(text=str(exc))

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
            display = [(r[1], r[2], r[3], r[4]) for r in rows]
            self._show_rows(tree, display,
                            ["שם חיה", "תאריך לידה", "תאריך ביקור", "סיבה"],
                            row_color="#0d2b1e")
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    # ── Tab 3: Procedure – Routine Checkups ──────────────────────────────────
    def _tab_procedure_checkups(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  📋  בדיקות שגרה  ")

        self._section_card(
            tab,
            title="⚙️ Process_Routine_Checkups",
            desc=(
                "יוצרת רשומות בריאות אוטומטיות לחיות שלא עברו בדיקה בשנה האחרונה. "
                "הפעלה בטוחה – ניתן להפעיל מספר פעמים."
            ),
            accent=_PROC_COLOR,
        )

        tree = self._result_tree(tab)
        self._run_button(tab, "▶  הפעל פרוצדורה",
                         command=lambda: self._run_checkups(tree),
                         color=_PROC_COLOR).pack(pady=8, ipadx=0)

    def _run_checkups(self, tree: ttk.Treeview):
        try:
            rows = call_procedure_refcursor("process_routine_checkups", ())
            if rows:
                names = _animal_name_map([int(r[4]) for r in rows])
                display = [
                    (r[1], r[2], r[3], names.get(int(r[4]), str(r[4])))
                    for r in rows
                ]
                self._show_rows(tree, display,
                                ["תאריך בדיקה", "משקל", "סטטוס", "שם חיה"],
                                row_color="#1a1a2e")
            else:
                self._show_rows(tree, [], None)
            messagebox.showinfo("הושלם", f"נוצרו {len(rows)} רשומות בריאות חדשות", parent=self)
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    # ── Tab 4: Procedure – Adjust Diet Cost ──────────────────────────────────
    def _tab_procedure_diet(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  🥗  עדכון עלות תזונה  ")

        self._section_card(
            tab,
            title="⚙️ Adjust_Diet_Cost_By_Species",
            desc="מעלה את עלות תוכניות התזונה לפי אחוז למין נבחר.",
            accent=_PROC_COLOR,
        )

        form = tk.Frame(tab, bg=BG)
        form.pack(fill=tk.X, padx=PAD, pady=4)

        tk.Label(form, text="מין:", bg=BG, fg=TEXT_MUTED, font=FONT_SMALL
                 ).grid(row=0, column=2, padx=8, pady=4)
        self.species_var = tk.StringVar()
        self.species_cb = ttk.Combobox(form, textvariable=self.species_var,
                                        width=30, state="readonly")
        self.species_cb.grid(row=0, column=1, pady=4)
        self._species_map: dict[str, int] = {}

        tk.Label(form, text="אחוז העלאה:", bg=BG, fg=TEXT_MUTED, font=FONT_SMALL
                 ).grid(row=1, column=2, padx=8, pady=4)
        self.pct_var = tk.StringVar(value="10")
        ttk.Entry(form, textvariable=self.pct_var, width=10).grid(row=1, column=1, pady=4)

        tree = self._result_tree(tab)
        self._run_button(tab, "▶  הפעל פרוצדורה",
                         command=lambda: self._run_adjust_diet(tree),
                         color=_PROC_COLOR).pack(pady=4)
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
            display = [(r[2], f"₪ {float(r[1]):.2f}") for r in rows]
            self._show_rows(tree, display,
                            ["שם תוכנית", "עלות יומית"],
                            row_color="#1a1a2e")
            messagebox.showinfo("הושלם", "עלויות התזונה עודכנו", parent=self)
        except (psycopg2.Error, DatabaseError) as exc:
            self._show_proc_error(exc)

    # ── Tab 5: Trigger Demo ───────────────────────────────────────────────────
    def _tab_trigger_demo(self, nb):
        tab = tk.Frame(nb, bg=BG)
        nb.add(tab, text="  ⚡  הדגמת Triggers  ")

        self._section_card(
            tab,
            title="⚡ Trg_Habitat_Capacity_Log  &  Trg_Prevent_Invalid_Medical_Cost",
            desc=(
                "עדכון MaxCapacity בטבלת habitat מפעיל Trg_Habitat_Capacity_Log ומתעד ביומן. "
                "| עדכון Cost > 500 ב-medicalvisit ללא Summary חוסם את הפעולה."
            ),
            accent=_TRIG_COLOR,
        )

        # Capacity update sub-form
        lf = tk.Frame(tab, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        lf.pack(fill=tk.X, padx=PAD, pady=(4, 8))

        tk.Label(lf, text="עדכון קיבולת → יומן", bg=BG2, fg=_TRIG_COLOR,
                 font=FONT_HEAD).pack(anchor="e", padx=PAD, pady=(8, 4))

        ctrl = tk.Frame(lf, bg=BG2)
        ctrl.pack(fill=tk.X, padx=PAD, pady=(0, 8))

        self.cap_habitat = tk.StringVar()
        self.cap_habitat_cb = ttk.Combobox(ctrl, textvariable=self.cap_habitat,
                                            width=32, state="readonly")
        self.cap_habitat_cb.pack(side=tk.RIGHT, padx=(0, 8))

        tk.Label(ctrl, text="קיבולת חדשה:", bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL
                 ).pack(side=tk.RIGHT)
        self.cap_value = tk.StringVar(value="100")
        ttk.Entry(ctrl, textvariable=self.cap_value, width=8).pack(side=tk.RIGHT, padx=4)

        self._run_button(ctrl, "⚡  עדכן והצג יומן",
                         command=self._demo_capacity_trigger,
                         color=_TRIG_COLOR).pack(side=tk.LEFT, ipadx=8, ipady=4)

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

        # Log treeview
        tk.Label(tab, text="יומן שינויי קיבולת (5 רשומות אחרונות):",
                 bg=BG, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="e", padx=PAD)
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
                cur.execute(
                    "UPDATE habitat SET maxcapacity = %s WHERE habitatid = %s",
                    (cap, hid),
                )
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
                ["בית גידול", "קיבולת קודמת", "קיבולת חדשה", "תאריך"],
                row_color="#2b1f0a",
            )
        except psycopg2.Error as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
    return f"#{r:02x}{g:02x}{b:02x}"
