import flet as ft
import threading
import time

TITLE_FONT_SIZE = 30
BODY_FONT_SIZE = 18
CARD_WIDTH = 1000
CARD_HEIGHT = 650

def guideline_tile(emoji, text):
    return ft.AnimatedSwitcher(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(emoji, size=BODY_FONT_SIZE + 6),
                    ft.Text(
                        text,
                        size=BODY_FONT_SIZE,
                        color=ft.colors.BLACK87,
                        expand=True,
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=0.5,
                color=ft.colors.GREY_300,
                offset=ft.Offset(1, 2)
            ),
            margin=ft.margin.only(bottom=12)
        ),
        duration=500
    )

def build_guidelines_frame(app):
    # Emoji-based guidelines
    guidelines = [
        ("💡", "Ensure good lighting so the child’s face is clearly visible."),
        ("👂", "Encourage the child to listen and respond to TellO’s prompts."),
        ("👀", "Keep eyes on the screen to see the images related to the story."),
        ("🗣️", "Speak clearly and loudly so TellO can hear properly."),
        ("🎉", "Enjoy the story! Have fun and engage with TellO.")
    ]

    # Scrollable guideline area
    scrollable_guidelines = ft.ListView(
        controls=[guideline_tile(emoji, text) for emoji, text in guidelines],
        expand=True,
        spacing=5,
        padding=0,
        auto_scroll=False
    )

    # Proceed button
    proceed_button = ft.ElevatedButton(
        content=ft.Text("Proceed", size=BODY_FONT_SIZE + 1),
        bgcolor=ft.colors.INDIGO_300,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=25, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda e: app.next_frame(),  # Use app controller to move to next frame
    )

    return ft.Container(
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
        bgcolor=ft.colors.PURPLE_50,
        padding=20,
        border_radius=20,
        shadow=ft.BoxShadow(
            blur_radius=25,
            spread_radius=2,
            color=ft.colors.GREY_300,
            offset=ft.Offset(2, 3)
        ),
        content=ft.Column(
            controls=[
                # Title + Mascot
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Before We Begin...", size=TITLE_FONT_SIZE, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                                ft.Text("Please follow these simple guidelines for the best experience with TellO:", size=BODY_FONT_SIZE, color=ft.colors.BLACK54),
                            ],
                            expand=2,
                            spacing=10
                        ),
                        ft.Image(
                            src="https://i.pinimg.com/736x/c4/17/09/c41709926b5957ee80d2f2232e7b8032.jpg",
                            width=90,
                            height=90,
                            border_radius=50,
                            fit=ft.ImageFit.CONTAIN
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),

                ft.Divider(height=10, color=ft.colors.TRANSPARENT),

                # Scrollable list
                ft.Container(content=scrollable_guidelines, expand=True),

                ft.Divider(height=10, color=ft.colors.TRANSPARENT),

                # Proceed button
                ft.Row(
                    controls=[proceed_button],
                    alignment=ft.MainAxisAlignment.END,
                )
            ],
            spacing=15,
            expand=True
        ),
        visible=False  
    )

def build_loading_frame(app):
    # Create components
    progress = ft.ProgressBar(
        width=300, color=ft.colors.AMBER, bgcolor=ft.colors.BROWN_100)
    text = ft.Text("Loading......", size=20,
                   weight=ft.FontWeight.NORMAL, color=ft.colors.BROWN_600)

    mascot = ft.Image(
        src="https://i.pinimg.com/originals/20/5b/0f/205b0f55dc999a06b6d34ec78c8724bd.gif",
        width=400,
        height=300,
        fit=ft.ImageFit.CONTAIN,
    )

    centered_container = ft.Container(
        width=800,
        bgcolor=ft.colors.WHITE,
        border_radius=20,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=4,
            blur_radius=10,
            color=ft.colors.BLACK26,
            offset=ft.Offset(0, 4),
        ),
        padding=30,
        content=ft.Column(
            controls=[
                mascot,
                ft.Container(height=20),
                progress,
                ft.Container(height=10),
                text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    )

    # Create a full-screen container to hold the content
    full_screen_center = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=centered_container,
        visible=False
    )

    # Define a synchronous on_show handler that schedules a frame transition after 3 seconds.
    def on_show_sync():
        app.frames["Storytelling"].start_video()
        threading.Thread(
            target=app.run_storytelling, 
            args=(app.frames["Storytelling"],), 
            daemon=True
        ).start()

        # This function runs in a separate thread so as not to block the UI.
        def switch_frame_after_delay():
            time.sleep(2)
            app.next_frame()
            app.page.update()
        threading.Thread(target=switch_frame_after_delay, daemon=True).start()

    full_screen_center.on_show = on_show_sync

    return full_screen_center
