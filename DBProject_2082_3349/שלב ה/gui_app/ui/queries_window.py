"""Phase B analytical queries window – dark mode redesign."""
import tkinter as tk
from tkinter import messagebox, ttk

from database import DatabaseError, fetch_all
from queries_data import PHASE_B_QUERIES
from ui.styles import (
    ACCENT, BG, BG2, BG3, BORDER,
    FONT_BODY, FONT_HEAD, FONT_SMALL, FONT_TITLE,
    PAD, PRIMARY, PRIMARY_LT, TEXT, TEXT_MUTED, TEXT_DIM,
    SUCCESS, DANGER, configure_styles, tag_treeview_rows,
)

_QUERY_ICONS = {
    "food_by_species":       "🥦",
    "habitat_missing_checkups": "🏕️",
    "diet_cost_april":       "📊",
    "weight_december":       "⚖️",
}

_QUERY_COLORS = [PRIMARY, ACCENT, "#a29bfe", "#74b9ff"]


class QueriesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 שאילתות – שלב ב'")
        self.configure(bg=BG)
        self.geometry("1020x640")
        self.minsize(800, 500)
        configure_styles(self)

        self._keys = list(PHASE_B_QUERIES.keys())
        self._selected_idx = 0

        self._build_header()
        self._build_body()

        # Auto-select first
        if self._keys:
            self._select(0)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#111e2d", height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📊  שאילתות ניתוח – שלב ב'",
                 bg="#111e2d", fg=PRIMARY_LT, font=FONT_TITLE,
                 anchor="e").pack(side=tk.RIGHT, padx=PAD)
        tk.Button(hdr, text="✕  סגור", bg=BG3, fg=TEXT_MUTED,
                  font=FONT_SMALL, relief="flat", cursor="hand2",
                  command=self.destroy).pack(side=tk.LEFT, padx=PAD, pady=10, ipadx=8)

    # ── Body: left cards + right results ─────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        # ── Left panel: query cards ──────────────────────────────────────────
        left = tk.Frame(body, bg="#111e2d", width=290)
        left.pack(side=tk.RIGHT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(left, text="בחר שאילתה", bg="#111e2d", fg=TEXT_MUTED,
                 font=FONT_SMALL, anchor="e").pack(fill=tk.X, padx=PAD, pady=(PAD, 6))

        self._card_frames: list[tk.Frame] = []
        for i, key in enumerate(self._keys):
            q = PHASE_B_QUERIES[key]
            icon = _QUERY_ICONS.get(key, "🔍")
            color = _QUERY_COLORS[i % len(_QUERY_COLORS)]
            card = self._make_query_card(left, i, icon, q["title"], q["description"], color)
            card.pack(fill=tk.X, padx=8, pady=4)
            self._card_frames.append(card)

        # Run button
        _RunBtn(left, text="▶  הרץ שאילתה", command=self._run
                ).pack(fill=tk.X, padx=8, pady=PAD, ipadx=0, ipady=8)

        # ── Right panel: results ─────────────────────────────────────────────
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Description bar
        desc_card = tk.Frame(right, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        desc_card.pack(fill=tk.X, pady=(0, 8))

        self.query_title_lbl = tk.Label(desc_card, text="",
                                         bg=BG2, fg=PRIMARY_LT, font=FONT_HEAD,
                                         anchor="e", padx=PAD, pady=8)
        self.query_title_lbl.pack(anchor="e")

        self.desc_lbl = tk.Label(desc_card, text="",
                                  bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL,
                                  wraplength=620, justify="right", anchor="e",
                                  padx=PAD, pady=(0, 8))
        self.desc_lbl.pack(anchor="e")

        # Result count
        self.result_count = tk.Label(right, text="",
                                      bg=BG, fg=TEXT_DIM, font=FONT_SMALL, anchor="w")
        self.result_count.pack(anchor="w", padx=4)

        # Treeview
        tv_frame = tk.Frame(right, bg=BG)
        tv_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tv_frame, show="headings")
        vsb = ttk.Scrollbar(tv_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tv_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

    # ── Query card ────────────────────────────────────────────────────────────
    def _make_query_card(self, parent, idx, icon, title, desc, accent_color) -> tk.Frame:
        card = tk.Frame(parent, bg=BG2, cursor="hand2",
                        highlightbackground=BORDER, highlightthickness=1)

        stripe = tk.Frame(card, bg=accent_color, width=4)
        stripe.pack(side=tk.RIGHT, fill=tk.Y)

        content = tk.Frame(card, bg=BG2)
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        tk.Label(content, text=f"{icon}  {title}",
                 bg=BG2, fg=TEXT, font=FONT_SMALL,
                 anchor="e", wraplength=220, justify="right").pack(anchor="e")
        tk.Label(content, text=desc,
                 bg=BG2, fg=TEXT_MUTED, font=("Segoe UI", 8),
                 anchor="e", wraplength=220, justify="right").pack(anchor="e")

        def bind_click(w, i=idx):
            w.bind("<Button-1>", lambda _: self._select(i))
            w.bind("<Enter>",    lambda _: self._card_hover(i, True))
            w.bind("<Leave>",    lambda _: self._card_hover(i, False))
            for child in w.winfo_children():
                bind_click(child, i)

        bind_click(card)
        return card

    def _select(self, idx: int):
        self._selected_idx = idx
        for i, card in enumerate(self._card_frames):
            is_sel = (i == idx)
            bg = BG3 if is_sel else BG2
            hl = PRIMARY if is_sel else BORDER
            card.configure(bg=bg, highlightbackground=hl)
            for child in card.winfo_children():
                try:
                    child.configure(bg=bg)
                    for gc in child.winfo_children():
                        gc.configure(bg=bg)
                except Exception:
                    pass

        key = self._keys[idx]
        q = PHASE_B_QUERIES[key]
        self.query_title_lbl.configure(text=q["title"])
        self.desc_lbl.configure(text=q["description"])
        self.result_count.configure(text="")

    def _card_hover(self, idx: int, on: bool):
        if idx == self._selected_idx:
            return
        bg = BG3 if on else BG2
        card = self._card_frames[idx]
        card.configure(bg=bg)
        for child in card.winfo_children():
            try:
                child.configure(bg=bg)
                for gc in child.winfo_children():
                    gc.configure(bg=bg)
            except Exception:
                pass

    # ── Run query ─────────────────────────────────────────────────────────────
    def _run(self):
        key = self._keys[self._selected_idx]
        q = PHASE_B_QUERIES[key]

        self.tree.delete(*self.tree.get_children())
        self.result_count.configure(text="מריץ שאילתה...")
        self.update_idletasks()

        try:
            rows = fetch_all(q["sql"])
        except DatabaseError as exc:
            messagebox.showerror("שגיאה", str(exc), parent=self)
            self.result_count.configure(text="❌ שגיאה")
            return

        if not rows:
            self.tree["columns"] = ["msg"]
            self.tree.heading("msg", text="הודעה")
            self.tree.column("msg", width=500)
            self.tree.insert("", tk.END, values=(
                "אין תוצאות – ייתכן שאין נתונים. ודאו חיבור ל-zoo_db",))
            self.result_count.configure(text="0 תוצאות")
            return

        # Use meaningful column headers derived from first row
        col_labels = _infer_headers(key, len(rows[0]))
        cols = [f"c{i}" for i in range(len(col_labels))]
        self.tree["columns"] = cols
        for col_id, label in zip(cols, col_labels):
            self.tree.heading(col_id, text=label)
            self.tree.column(col_id, width=160, anchor=tk.CENTER)

        self.tree.tag_configure("odd",  background="#1f2f44", foreground=TEXT)
        self.tree.tag_configure("even", background="#1a2535", foreground=TEXT)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END,
                             values=[str(v) for v in row],
                             tags=(tag,))

        self.result_count.configure(text=f"✅  {len(rows)} תוצאות")


def _infer_headers(query_key: str, ncols: int) -> list[str]:
    """Return Hebrew column headers for known queries."""
    map_ = {
        "food_by_species":           ["שם נפוץ", "שם מדעי", "סך מזון"],
        "habitat_missing_checkups":  ["שם בית גידול", "סוג אקלים", "מספר חיות"],
        "diet_cost_april":           ["שם נפוץ", "שם מדעי", "סך עלות תזונה"],
        "weight_december":           ["שם בית גידול", "סוג אקלים", "סך משקל"],
    }
    labels = map_.get(query_key, [f"עמודה {i + 1}" for i in range(ncols)])
    # Pad / trim to match actual ncols
    while len(labels) < ncols:
        labels.append(f"עמודה {len(labels) + 1}")
    return labels[:ncols]


class _RunBtn(tk.Label):
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent, text=text, bg=PRIMARY, fg="white",
                         font=FONT_HEAD, cursor="hand2", relief="flat", **kw)
        self.bind("<Enter>", lambda _: self.configure(bg="#00a07a"))
        self.bind("<Leave>", lambda _: self.configure(bg=PRIMARY))
        self.bind("<Button-1>", lambda _: command())
