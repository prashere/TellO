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

                # Store student ID and name together as tuples
                self.students = [(student["studentid"], student["studentname"])
                                 for student in student_data]

                if self.students:
                    # Extract only names for the dropdown display
                    self.student_dropdown["values"] = [
                        name for _, name in self.students]

                    # Set default selection
                    self.selected_student.set(self.students[0][1])
                else:
                    self.student_dropdown["values"] = ["No students found"]
                    self.selected_student.set("No students found")
            else:
                messagebox.showerror("Error", "Failed to fetch students")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Server Error: {e}")

    def confirm_selection(self):
        """Proceed only if a valid student is selected."""
        selected_student_name = self.selected_student.get()

        if selected_student_name == "No students found" or not selected_student_name:
            messagebox.showwarning("Warning", "Please select a valid student.")
            return

        # Retrieve student ID dynamically from the stored (ID, Name) tuples
        selected_student_id = next(
            (sid for sid, name in self.students if name == selected_student_name), None)

        if not selected_student_id:
            messagebox.showerror("Error", "Selected student ID not found.")
            return

        # Store selected student ID in the controller for further use
        self.controller.selected_student_id = selected_student_id

        messagebox.showinfo("Selection Confirmed",
                            f"Selected Student: {selected_student_name}")
        self.controller.next_frame("StudentSelection")  # Proceed to next frame
