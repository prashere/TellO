import flet as ft

def build_end_session_frame(app):
    def view_report(e):
        app.page.launch_url("http://127.0.0.1:8000/report_list/")

    # def view_report(e):
    #     dlg = ft.AlertDialog(
    #         title=ft.Text("Report", size=20, weight=ft.FontWeight.BOLD),
    #         content=ft.Text("Report opened!"),
    #         actions=[ft.TextButton("OK", on_click=lambda e: dlg.close())],
    #     )
    #     app.page.dialog = dlg
    #     dlg.open = True
    #     app.page.update()

    celebration_img = ft.Image(
        src="https://i.pinimg.com/originals/53/a0/ad/53a0ad64786c712c95c757714c38c8b4.gif",
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
    )

    session_ended_text = ft.Text(
        "🎉 Session Completed!",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLUE_GREY_900,
        text_align=ft.TextAlign.CENTER,
    )

    thank_you_text = ft.Text(
        "Thank you for joining the session.\nWe hope you enjoyed it!",
        size=20,
        color=ft.colors.BLUE_GREY_700,
        text_align=ft.TextAlign.CENTER,
    )

    view_report_button = ft.ElevatedButton(
        text="📄 View Session Report",
        on_click=view_report,
        bgcolor=ft.colors.AMBER_300,
        color=ft.colors.BLACK,
        height=50,
        width=250,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    content_card = ft.Container(
        content=ft.Column(
            controls=[
                celebration_img,
                session_ended_text,
                thank_you_text,
                ft.Container(height=20),
                view_report_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        width=500,
        padding=30,
        border_radius=20,
        bgcolor=ft.colors.WHITE,
        shadow=ft.BoxShadow(
            blur_radius=15, spread_radius=2,
            color=ft.colors.GREY_400, offset=ft.Offset(3, 5)
        ),
    )

    end_session_container = ft.Container(
        expand=True,
        bgcolor=ft.colors.BLUE_50,
        alignment=ft.alignment.center,
        content=content_card,
        visible=False
    )

    return end_session_container
