import tkinter as tk
from ui_assets.constants import SOFT_BLUE, SOFT_YELLOW, WHITE, SOFT_PINK, SOFT_GREEN, DARK_TEXT, FONT, TITLE_FONT

class TeacherVerificationFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_BLUE)

        content_frame = tk.Frame(self, bg=SOFT_BLUE)
        content_frame.pack(expand=True)

        # Logo
        logo_label = tk.Label(content_frame, image=controller.logo_img, bg=SOFT_BLUE)
        logo_label.pack(pady=20)

        # Title
        tk.Label(content_frame, text="Teacher Verification", font=TITLE_FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack()

        # Username Field
        username_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:", font=FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        tk.Entry(username_frame, font=FONT).pack(side="left")

        # Password Field
        password_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        password_frame.pack(pady=10)
        tk.Label(password_frame, text="Password:", font=FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        tk.Entry(password_frame, font=FONT, show="*").pack(side="left")

        # Login Button
        tk.Button(content_frame, text="Login", font=FONT, bg=SOFT_YELLOW, command=lambda: controller.next_frame("TeacherVerification")).pack(pady=20)
