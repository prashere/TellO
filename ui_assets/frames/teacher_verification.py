import tkinter as tk
from ui_assets.constants import SOFT_BLUE, SOFT_YELLOW, WHITE, SOFT_PINK, SOFT_GREEN, DARK_TEXT, FONT, TITLE_FONT
import requests
from tkinter import messagebox


class TeacherVerificationFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_BLUE)
        self.controller = controller

        content_frame = tk.Frame(self, bg=SOFT_BLUE)
        content_frame.pack(expand=True)

        # Logo
        logo_label = tk.Label(
            content_frame, image=controller.logo_img, bg=SOFT_BLUE)
        logo_label.pack(pady=20)

        # Title
        tk.Label(content_frame, text="Teacher Verification",
                 font=TITLE_FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack()

        # # Username Field
        # username_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        # username_frame.pack(pady=10)
        # tk.Label(username_frame, text="Username:", font=FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        # tk.Entry(username_frame, font=FONT).pack(side="left")

        # # Password Field
        # password_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        # password_frame.pack(pady=10)
        # tk.Label(password_frame, text="Password:", font=FONT, bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        # tk.Entry(password_frame, font=FONT, show="*").pack(side="left")

        # # Login Button
        # tk.Button(content_frame, text="Login", font=FONT, bg=SOFT_YELLOW, command=lambda: controller.next_frame("TeacherVerification")).pack(pady=20)

        # Username Field
        username_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:", font=FONT,
                 bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        # Store entry field reference
        self.username_entry = tk.Entry(username_frame, font=FONT)
        self.username_entry.pack(side="left")

        # Password Field
        password_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        password_frame.pack(pady=10)
        tk.Label(password_frame, text="Password:", font=FONT,
                 bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        # Store entry field reference
        self.password_entry = tk.Entry(password_frame, font=FONT, show="*")
        self.password_entry.pack(side="left")

        # Login Button
        tk.Button(content_frame, text="Login", font=FONT, bg=SOFT_YELLOW,
                  command=self.authenticate_teacher).pack(pady=20)

    def authenticate_teacher(self):
        """Authenticate teacher using Django backend API."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        url = "http://127.0.0.1:8000/api/teacher-login/"  # Adjust for deployed API
        data = {"username": username, "password": password}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                teacher_id = response.json().get("teacher_id")
                messagebox.showinfo("Login Successful",
                                    f"Welcome! Teacher ID: {teacher_id}")

                # Store teacher_id in controller for later use if needed
                self.controller.teacher_id = teacher_id

                # Proceed to the next frame
                # Replace with actual frame name
                self.controller.next_frame("TeacherVerification")
            elif response.status_code == 403:
                messagebox.showerror(
                    "Access Denied", "You are not registered as a teacher.")
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Server Error: {e}")
