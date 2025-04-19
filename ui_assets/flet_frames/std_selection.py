import flet as ft
import requests
from flet import colors as Colors

PASTEL_YELLOW_BG = Colors.BLUE_50


def build_student_selection_frame(app):
    page = app.page
    page.title = "Student Selection"
    page.window_width = 900
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = PASTEL_YELLOW_BG
    page.padding = 20

    teacher_id = app.teacher_id
    student_options = []
    selected_student = ft.Ref[ft.Dropdown]()
    feedback_text = ft.Text("", color=Colors.RED_400, size=20)

    def fetch_students():
        nonlocal teacher_id
        teacher_id = app.teacher_id
        username = app.username

        print("username :: ", username)

        if not teacher_id:
            feedback_text.value = "Teacher ID not found. Please log in again."
            page.update()
            return

        url = f"http://127.0.0.1:8000/api/get-students/{teacher_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json().get("students", [])
                if data:
                    student_list = [(s["studentid"], s["studentname"])
                                    for s in data]
                    app.student_name_id_map = {
                        name: sid for sid, name in student_list}
                    student_options.clear()
                    for sid, name in student_list:
                        student_options.append(ft.dropdown.Option(name))
                    selected_student.current.options = student_options
                    selected_student.current.value = student_options[0].key if student_options else None
                    feedback_text.value = ""
                else:
                    student_options.clear()
                    selected_student.current.options = []
                    selected_student.current.value = None
                    feedback_text.value = "No students found."
            else:
                feedback_text.value = "Failed to fetch students."
        except requests.exceptions.RequestException as e:
            feedback_text.value = f"Server Error: {e}"

        page.update()

    def confirm_selection(e):
        stud_name = selected_student.current.value
        if not stud_name or stud_name == "No students found":
            feedback_text.value = "Please select a valid student."
            page.update()
            return

        app.selected_student_id = app.student_name_id_map.get(stud_name)

        feedback_text.value = f"Student '{stud_name}' selection confirmed!"
        page.snack_bar = ft.SnackBar(ft.Text("Proceeding to next page..."))
        app.show_frame("Guidelines")
        page.snack_bar.open = True
        page.update()

    def reset_fields(e):
        selected_student.current.value = None
        feedback_text.value = ""
        page.update()

    title_text = ft.Text(
        "Student Selection 🎈",
        weight=ft.FontWeight.BOLD,
        size=30,
        color=Colors.BLACK,
        text_align="center"
    )

    instruction_text = ft.Text(
        "Please select a student from the list below:",
        size=18,
        color=Colors.BLUE_GREY_700,
        text_align="center"
    )

    # Student Dropdown
    student_dropdown = ft.Dropdown(
        ref=selected_student,
        width=350,
        options=[],
        hint_text="Select student...",
        text_size=20
    )

    # Load Button — below dropdown with rectangular style
    load_button = ft.ElevatedButton(
        "Load Students",
        on_click=lambda e: fetch_students(),
        height=45,
        width=200,
        bgcolor=Colors.BLUE_200,
    )

    # Reset and Confirm Buttons
    buttons_row = ft.Row(
        [
            ft.ElevatedButton(
                "Reset", on_click=reset_fields,
                bgcolor=Colors.BLUE_GREY_50,
                color=Colors.BLACK,
                height=45,
                width=150
            ),
            ft.ElevatedButton(
                "Confirm Selection", on_click=confirm_selection,
                bgcolor=Colors.AMBER_300,
                color=Colors.BLACK,
                height=45,
                width=200
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Horizontal divider (nice line)
    def get_divider():
        return ft.Divider(height=1, thickness=2, color=Colors.GREY_300)

    content_card = ft.Container(
        content=ft.Column(
            [
                title_text,
                get_divider(),
                instruction_text,
                student_dropdown,
                load_button,
                get_divider(),
                buttons_row,
                feedback_text,
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=500,
        bgcolor=Colors.WHITE,
        padding=30,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1,
                            color=Colors.GREY_400, offset=ft.Offset(2, 2)),
    )

    student_selection_container = ft.Container(
        content=ft.Column(
            [content_card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        visible=False
    )

    def on_show():
        fetch_students()

    student_selection_container.on_show = on_show

    return student_selection_container
