"""Initial database connection settings dialog."""
import tkinter as tk
from tkinter import messagebox, ttk

import config
from database import DatabaseError, test_connection
from ui.styles import BG, CARD, FONT_BODY, FONT_HEAD, PRIMARY


class ConnectionDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("התחברות לבסיס הנתונים")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        frame = ttk.Frame(self, style="Card.TFrame", padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        fields = [
            ("host", "שרת (Host)", config.DB_CONFIG["host"]),
            ("port", "פורט", str(config.DB_CONFIG["port"])),
            ("dbname", "שם בסיס נתונים (zoo_db)", config.DB_CONFIG["dbname"]),
            ("user", "משתמש", config.DB_CONFIG["user"]),
            ("password", "סיסמה", config.DB_CONFIG["password"]),
        ]
        hint = ttk.Label(
            frame,
            text="חשוב: בסיס הנתונים עם הנתונים הוא zoo_db (לא postgres)",
            style="Card.TLabel",
            foreground="#c0392b",
        )
        self.vars = {}
        for i, (key, label, default) in enumerate(fields):
            ttk.Label(frame, text=label, style="Card.TLabel", font=FONT_BODY).grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=4
            )
            var = tk.StringVar(value=default)
            self.vars[key] = var
            show = "*" if key == "password" else None
            ttk.Entry(frame, textvariable=var, width=28, show=show).grid(
                row=i, column=1, pady=4
            )

        hint.grid(row=len(fields), column=0, columnspan=2, pady=(8, 0))

        btn_row = ttk.Frame(frame, style="Card.TFrame")
        btn_row.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(btn_row, text="בדיקת חיבור", command=self._test).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="המשך", style="Primary.TButton", command=self._connect).pack(
            side=tk.RIGHT, padx=4
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _apply_config(self):
        config.DB_CONFIG["host"] = self.vars["host"].get().strip()
        config.DB_CONFIG["port"] = int(self.vars["port"].get().strip())
        config.DB_CONFIG["dbname"] = self.vars["dbname"].get().strip()
        config.DB_CONFIG["user"] = self.vars["user"].get().strip()
        config.DB_CONFIG["password"] = self.vars["password"].get()

    def _test(self):
        self._apply_config()
        try:
            msg = test_connection()
            messagebox.showinfo("חיבור תקין", msg, parent=self)
        except DatabaseError as exc:
            messagebox.showerror("שגיאת חיבור", str(exc), parent=self)

    def _connect(self):
        self._apply_config()
        try:
            test_connection()
        except DatabaseError as exc:
            messagebox.showerror("שגיאת חיבור", str(exc), parent=self)
            return
        self.on_success()
        self.destroy()

    def _cancel(self):
        self.master.destroy()
