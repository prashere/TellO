from ui_assets.flet_frames.flet_app import MyApp
import flet as ft
import asyncio

loop = asyncio.get_event_loop()

def main(page: ft.Page):
    page.window_width = 900
    page.window_height = 500
    page.padding = 0
    app = MyApp(page)
    app.event_loop = loop


ft.app(target=main)
