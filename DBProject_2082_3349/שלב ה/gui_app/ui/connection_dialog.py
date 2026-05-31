"""Full-screen splash login dialog with animated canvas background."""
import math
import tkinter as tk
from tkinter import messagebox, ttk

import config
from database import DatabaseError, test_connection
from ui.styles import (
    ACCENT, BG, BG2, BG3, BORDER, FONT_BODY, FONT_HEAD, FONT_SMALL,
    FONT_TITLE, FONT_DISPLAY, PAD, PRIMARY, PRIMARY_DK, PRIMARY_LT,
    TEXT, TEXT_MUTED, configure_styles,
)


class ConnectionDialog(tk.Toplevel):
    """Full-screen dark-mode login splash."""

    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Zoo Management – התחברות")
        self.configure(bg=BG)

        # Go nearly full-screen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = min(sw, 1100), min(sh, 720)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.resizable(True, True)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._anim_angle = 0
        self._connecting = False

        # ── Canvas background with animated decorations ──────────────────────
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._draw_background()
        self._build_card()

        # Start animation loop
        self._animate()

    # ── Background drawing ────────────────────────────────────────────────────
    def _draw_background(self):
        c = self.canvas
        c.delete("bg")
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 720

        # Draw large subtle geometric circles (using dim solid colors – Tkinter has no alpha)
        # Green rings bottom-left: progressively brighter for inner rings
        green_shades = ["#162e28", "#1a3b32", "#1e493c", "#225748"]
        for r, color in zip([350, 280, 200, 130], green_shades):
            cx, cy = w * 0.15, h * 0.85
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          outline=color, width=1, tags="bg")

        # Gold rings top-right
        gold_shades = ["#2b2000", "#332600", "#3d2e00"]
        for r, color in zip([300, 220, 140], gold_shades):
            cx, cy = w * 0.88, h * 0.12
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          outline=color, width=1, tags="bg")

        # Horizontal gradient stripe at top
        for i in range(4):
            shade = 20 + i * 8
            c.create_rectangle(0, i * 2, w, i * 2 + 2,
                                fill=f"#{shade:02x}{shade + 5:02x}{shade + 15:02x}",
                                outline="", tags="bg")

    def _animate(self):
        if not self.winfo_exists():
            return
        self._anim_angle = (self._anim_angle + 0.4) % 360
        c = self.canvas
        c.delete("anim")
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 720

        # Rotating dashed orbit ring bottom-left
        cx, cy, r = w * 0.15, h * 0.85, 350
        start = self._anim_angle
        c.create_arc(cx - r, cy - r, cx + r, cy + r,
                     start=start, extent=80,
                     style="arc", outline=PRIMARY, width=2, tags="anim")
        c.create_arc(cx - r, cy - r, cx + r, cy + r,
                     start=start + 100, extent=50,
                     style="arc", outline=PRIMARY_LT, width=1, tags="anim")

        # Rotating ring top-right
        cx2, cy2, r2 = w * 0.88, h * 0.12, 300
        c.create_arc(cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2,
                     start=360 - start, extent=100,
                     style="arc", outline=ACCENT, width=2, tags="anim")

        # Floating dots along a sine wave
        for i in range(6):
            angle_rad = math.radians(self._anim_angle + i * 60)
            dot_x = w * 0.15 + math.cos(angle_rad) * 350
            dot_y = h * 0.85 + math.sin(angle_rad) * 350
            if 0 <= dot_x <= w and 0 <= dot_y <= h:
                c.create_oval(dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4,
                              fill=PRIMARY, outline="", tags="anim")

        self.after(30, self._animate)

    def _build_card(self):
        # Central card frame placed via place (not pack/grid so it floats over canvas)
        card = tk.Frame(self.canvas, bg=BG2, highlightbackground=BORDER,
                        highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420)

        # ── Logo / header ───────────────────────────────────────────────────
        header = tk.Frame(card, bg=PRIMARY, height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Animal emoji + title inside header
        tk.Label(header, text="🦁", bg=PRIMARY, font=("Segoe UI", 28)).pack(
            side=tk.RIGHT, padx=(0, 12), pady=10)
        title_f = tk.Frame(header, bg=PRIMARY)
        title_f.pack(side=tk.RIGHT, pady=10, padx=12)
        tk.Label(title_f, text="Zoo Management", bg=PRIMARY,
                 fg="white", font=FONT_TITLE).pack(anchor="e")
        tk.Label(title_f, text="מערכת ניהול גן החיות", bg=PRIMARY,
                 fg="#b3ffe8", font=FONT_SMALL).pack(anchor="e")

        # ── Form body ────────────────────────────────────────────────────────
        body = tk.Frame(card, bg=BG2, padx=PAD * 2, pady=PAD)
        body.pack(fill=tk.X)

        fields = [
            ("host",     "🌐  שרת (Host)",          config.DB_CONFIG["host"]),
            ("port",     "🔌  פורט",                 str(config.DB_CONFIG["port"])),
            ("dbname",   "🗄️  בסיס נתונים",         config.DB_CONFIG["dbname"]),
            ("user",     "👤  משתמש",                config.DB_CONFIG["user"]),
            ("password", "🔑  סיסמה",               config.DB_CONFIG["password"]),
        ]
        self.vars = {}

        for key, label, default in fields:
            lbl = tk.Label(body, text=label, bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL,
                           anchor="e")
            lbl.pack(fill=tk.X, pady=(8, 0))

            var = tk.StringVar(value=default)
            self.vars[key] = var
            show = "*" if key == "password" else None
            entry = ttk.Entry(body, textvariable=var, show=show, font=FONT_BODY)
            entry.pack(fill=tk.X, ipady=3)

        # Hint
        hint = tk.Label(body,
                        text="💡 ודאו שבסיס הנתונים הוא zoo_db",
                        bg=BG2, fg=ACCENT, font=FONT_SMALL, anchor="e")
        hint.pack(fill=tk.X, pady=(10, 4))

        # ── Status line ───────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(body, textvariable=self.status_var,
                                   bg=BG2, fg=TEXT_MUTED, font=FONT_SMALL,
                                   anchor="e", wraplength=360)
        self.status_lbl.pack(fill=tk.X, pady=(2, 8))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = tk.Frame(card, bg=BG2, pady=PAD)
        btn_row.pack(fill=tk.X, padx=PAD * 2)

        self.connect_btn = _SplashButton(
            btn_row, text="התחבר  →", command=self._connect,
            bg=PRIMARY, hover_bg=PRIMARY_DK, fg="white",
        )
        self.connect_btn.pack(side=tk.RIGHT, ipadx=16, ipady=6, padx=(4, 0))

        _SplashButton(
            btn_row, text="בדוק חיבור", command=self._test,
            bg=BG3, hover_bg=BORDER, fg=TEXT_MUTED,
        ).pack(side=tk.RIGHT, ipadx=10, ipady=6)

        # spacer at bottom
        tk.Frame(card, bg=BG2, height=PAD).pack()

    # ── Actions ───────────────────────────────────────────────────────────────
    def _apply_config(self):
        config.DB_CONFIG["host"]     = self.vars["host"].get().strip()
        config.DB_CONFIG["port"]     = int(self.vars["port"].get().strip() or "5432")
        config.DB_CONFIG["dbname"]   = self.vars["dbname"].get().strip()
        config.DB_CONFIG["user"]     = self.vars["user"].get().strip()
        config.DB_CONFIG["password"] = self.vars["password"].get()

    def _test(self):
        self._apply_config()
        self.status_var.set("בודק חיבור...")
        self.status_lbl.configure(fg=TEXT_MUTED)
        self.update_idletasks()
        try:
            msg = test_connection()
            self.status_var.set(f"✅ {msg}")
            self.status_lbl.configure(fg=PRIMARY)
        except DatabaseError as exc:
            self.status_var.set(f"❌ {exc}")
            self.status_lbl.configure(fg="#ff4757")

    def _connect(self):
        if self._connecting:
            return
        self._connecting = True
        self.connect_btn.configure(text="מתחבר...", state="disabled")
        self._apply_config()
        self.status_var.set("מתחבר לבסיס הנתונים...")
        self.status_lbl.configure(fg=TEXT_MUTED)
        self.update_idletasks()
        try:
            test_connection()
        except DatabaseError as exc:
            self.status_var.set(f"❌ {exc}")
            self.status_lbl.configure(fg="#ff4757")
            self.connect_btn.configure(text="התחבר  →", state="normal")
            self._connecting = False
            return
        self.on_success()
        self.destroy()

    def _cancel(self):
        self.master.destroy()


class _SplashButton(tk.Label):
    """Flat hover-animated button for the splash card."""

    def __init__(self, parent, text, command, bg, hover_bg, fg, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=FONT_HEAD, cursor="hand2",
                         relief="flat", **kw)
        self._bg = bg
        self._hbg = hover_bg
        self._fg = fg
        self._cmd = command
        self.bind("<Enter>",  lambda _: self.configure(bg=hover_bg))
        self.bind("<Leave>",  lambda _: self.configure(bg=bg))
        self.bind("<Button-1>", lambda _: command())
