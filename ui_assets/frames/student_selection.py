import tkinter as tk
from tkinter import ttk
from ui_assets.constants import SOFT_YELLOW, DARK_TEXT, FONT, TITLE_FONT, SOFT_GREEN

class StudentSelectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_YELLOW)

        tk.Label(self, text="Student Selection", font=TITLE_FONT, bg=SOFT_YELLOW, fg=DARK_TEXT).pack(pady=20)

        students = ["Alice", "Bob", "Charlie", "Diana"]
        selected_student = tk.StringVar(value=students[0])
        ttk.Combobox(self, textvariable=selected_student, values=students, font=FONT).pack(pady=10)

        tk.Button(self, text="Confirm Selection", font=FONT, bg=SOFT_GREEN, command=lambda: controller.next_frame("StudentSelection")).pack(pady=20)
