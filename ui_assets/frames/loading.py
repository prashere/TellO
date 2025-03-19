import tkinter as tk
from ui_assets.constants import SOFT_BLUE, SOFT_YELLOW, DARK_TEXT, FONT, TITLE_FONT


class LoadingFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_BLUE)
        self.controller = controller

        # Create a container frame to center content
        container = tk.Frame(self, bg=SOFT_BLUE)
        container.pack(expand=True, fill="both")

        # Center the container's content using pack options.
        # Loading message: Increase font size and weight for better readability.
        title = tk.Label(container,
                         text="Please wait, loading...",
                         # Increase font size and make bold
                         font=(FONT[0], 20, "bold"),
                         bg=SOFT_BLUE,
                         fg=DARK_TEXT)
        title.pack(pady=20)

        # Create a canvas for the spinner (revolving circle)
        self.canvas_size = 150  # Increased size for better visibility
        self.canvas = tk.Canvas(container,
                                width=self.canvas_size,
                                height=self.canvas_size,
                                bg=SOFT_BLUE,
                                highlightthickness=0)
        self.canvas.pack(pady=20)

        # Initial angle for rotation
        self.angle = 0

        # Create an arc with a larger width for a more prominent spinner.
        # extent of 90 degrees makes it look like a quarter circle that rotates.
        self.arc = self.canvas.create_arc(15, 15, self.canvas_size-15, self.canvas_size-15,
                                          start=self.angle, extent=90, width=8,
                                          style='arc', outline=SOFT_YELLOW)

        # Start the spinner animation
        self.animate_spinner()

    def animate_spinner(self):
        # Update the starting angle to create a spinning effect.
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        # Call animate_spinner again after 100ms
        self.after(100, self.animate_spinner)
