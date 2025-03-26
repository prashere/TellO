import tkinter as tk
from tkinter import ttk, messagebox
import requests
from ui_assets.constants import SOFT_YELLOW, DARK_TEXT, FONT, TITLE_FONT, SOFT_GREEN


class StudentSelectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_YELLOW)
        self.controller = controller  # Store controller reference
        self.students = []            # Placeholder for student list
        self.selected_student = tk.StringVar()  # Selected student variable

        tk.Label(self, text="Student Selection", font=TITLE_FONT,
                 bg=SOFT_YELLOW, fg=DARK_TEXT).pack(pady=20)

        # Dropdown for students
        self.student_dropdown = ttk.Combobox(
            self, textvariable=self.selected_student, font=FONT)
        self.student_dropdown.pack(pady=10)

        # Confirm button
        tk.Button(self, text="Confirm Selection", font=FONT,
                  bg=SOFT_GREEN, command=self.confirm_selection).pack(pady=20)

    def on_show(self):
        """Called when the frame is shown. Fetch students only then."""
        self.fetch_students()

    def fetch_students(self):
        """Fetch students assigned to the logged-in teacher."""
        teacher_id = getattr(self.controller, "teacher_id", None)
        if not teacher_id:
            messagebox.showerror(
                "Error", "Teacher ID not found. Please log in again.")
            return

        url = f"http://127.0.0.1:8000/api/get-students/{teacher_id}/"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                student_data = response.json().get("students", [])
                self.students = [student["studentname"]
                                 for student in student_data]

                if self.students:
                    self.student_dropdown["values"] = self.students
                    # Set default selection
                    self.selected_student.set(self.students[0])
                else:
                    self.student_dropdown["values"] = ["No students found"]
                    self.selected_student.set("No students found")
            else:
                messagebox.showerror("Error", "Failed to fetch students")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Server Error: {e}")

    def confirm_selection(self):
        """Proceed only if a valid student is selected."""
        selected_student = self.selected_student.get()
        if selected_student == "No students found" or not selected_student:
            messagebox.showwarning("Warning", "Please select a valid student.")
            return

        messagebox.showinfo("Selection Confirmed",
                            f"Selected Student: {selected_student}")
        self.controller.next_frame("StudentSelection")  # Proceed to next frame
