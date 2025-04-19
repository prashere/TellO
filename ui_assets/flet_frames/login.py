import flet as ft
import requests
from flet import colors as Colors

TITLE_FONT_SIZE = 28
BODY_FONT_SIZE = 18


def build_teacher_verification_frame(app):
    page = app.page
    page.title = "Teacher Verification"
    page.bgcolor = Colors.BLUE_50
    page.window_width = 900
    page.window_height = 500
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.padding = 0

    # Image section (right panel)
    image_section = ft.Container(
        content=ft.Image(
            src="https://i.pinimg.com/736x/d5/96/bd/d596bd58a637a66db00c9aec01b82501.jpg", fit=ft.ImageFit.COVER),
        border_radius=ft.border_radius.only(top_right=30, bottom_right=30),
        expand=True,
        height=650,
        margin=ft.margin.only(right=20),
    )

    # Input fields
    username_input = ft.TextField(
        label="Username", border_radius=12, height=50, width=350)
    password_input = ft.TextField(label="Password", border_radius=12,
                                  height=50, width=350, password=True, can_reveal_password=True)

    success_text = ft.Text("", size=BODY_FONT_SIZE, color=Colors.GREEN_400)
    error_text = ft.Text("", color=Colors.RED_400)

    def login_clicked(e):
        username = username_input.value
        password = password_input.value

        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/teacher-login/",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                teacher_id = response.json().get("teacher_id")
                success_text.value = f"✅ Welcome! {username}"
                app.teacher_id = teacher_id
                app.username = username
                app.show_frame("StudentSelection")
                error_text.value = ""
            elif response.status_code == 403:
                success_text.value = ""
                error_text.value = "❌ You are not registered as a teacher."
            else:
                success_text.value = ""
                error_text.value = "❌ Invalid credentials."
        except Exception as ex:
            success_text.value = ""
            error_text.value = f"⚠️ Server error: {ex}"
        page.update()

    # Left login section (form)
    login_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Welcome back 👩🏻‍🦰", size=TITLE_FONT_SIZE,
                        weight="bold", color=Colors.BLACK),
                ft.Text("Please enter your details.",
                        size=16, color=Colors.BLUE_GREY_700),
                ft.Container(height=10),
                username_input,
                password_input,
                ft.Container(height=5),
                ft.Row([
                ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ElevatedButton("Log in", width=350, height=45, bgcolor=Colors.LIME_400,
                                  color=Colors.BLACK, on_click=login_clicked),
                success_text,
                error_text,
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Ready to start?"),
                    ft.TextButton("Storytelling", style=ft.ButtonStyle(
                        color=Colors.BLUE_700))
                ],
                    alignment=ft.MainAxisAlignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=Colors.WHITE,
        padding=30,
        margin=ft.margin.only(left=20),
        border_radius=ft.border_radius.only(top_left=30, bottom_left=30),
        width=500,
        height=650,
    )

    return ft.Container(
        content=ft.Row(
            controls=[login_card, image_section],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        visible=False  # Default to hidden
    )
