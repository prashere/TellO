import tkinter as tk
from tkinter import messagebox
from ui_assets.constants import SOFT_YELLOW, DARK_TEXT, FONT, TITLE_FONT, SOFT_BLUE

class EndSessionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_YELLOW)

        tk.Label(self, text="Session Ended", font=TITLE_FONT, bg=SOFT_YELLOW, fg=DARK_TEXT).pack(pady=20)
        tk.Label(self, text="Thank you for the session!", font=FONT, bg=SOFT_YELLOW, fg=DARK_TEXT).pack(pady=10)
        tk.Button(self, text="View Session Report", font=FONT, bg=SOFT_BLUE, command=lambda: messagebox.showinfo("Report", "Report opened!")).pack(pady=20)
