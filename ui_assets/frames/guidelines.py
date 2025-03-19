import tkinter as tk
from ui_assets.constants import SOFT_PINK, SOFT_YELLOW, DARK_TEXT, FONT, TITLE_FONT


class GuidelinesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_PINK)

        # Main content container with some border styling
        content_frame = tk.Frame(self, bg=SOFT_PINK, bd=2, relief="groove")
        content_frame.pack(expand=True, padx=30, pady=30)

        # Header for Guidelines with a contrasting border at the bottom
        header = tk.Label(content_frame,
                          text="Before We Begin, Please Follow These Guidelines:",
                          font=(TITLE_FONT[0], TITLE_FONT[1]+4, "bold"),
                          bg=SOFT_PINK,
                          fg=DARK_TEXT)
        header.pack(pady=(20, 10))
        tk.Frame(content_frame, bg=DARK_TEXT, height=2).pack(
            fill="x", padx=10, pady=(0, 20))

        # List of guidelines with bullet icons and subtle separators
        guidelines = [
            "Ensure Good Lighting – The child’s face should be well-lit and clearly visible.",
            "Follow TellO’s Instructions – Encourage the child to listen and respond when prompted.",
            "Watch the Screen – Images related to the story will appear here.",
            "Speak Clearly – The system listens and responds, so try to speak loudly and clearly.",
            "Enjoy the Story! – Have fun and engage with TellO for the best experience."
        ]

        for idx, guideline in enumerate(guidelines, start=1):
            # Create a container frame for each guideline
            guideline_frame = tk.Frame(content_frame, bg=SOFT_PINK)
            guideline_frame.pack(fill="x", padx=20, pady=5)

            # Bullet icon: using a blue circle emoji; adjust if needed.
            bullet = tk.Label(guideline_frame, text="🔵", font=(
                FONT[0], FONT[1]+4), bg=SOFT_PINK)
            bullet.pack(side="left", padx=(0, 10))

            # Guideline text
            lbl = tk.Label(guideline_frame,
                           text=f"{idx}) {guideline}",
                           font=(FONT[0], FONT[1]+2),
                           bg=SOFT_PINK,
                           fg=DARK_TEXT,
                           wraplength=700,
                           justify="left")
            lbl.pack(side="left", fill="x", expand=True)

            # Add a separator line below each guideline except the last one
            if idx < len(guidelines):
                separator = tk.Frame(content_frame, bg=DARK_TEXT, height=1)
                separator.pack(fill="x", padx=20, pady=(0, 5))

        # Proceed button with enhanced styling
        proceed_button = tk.Button(content_frame,
                                   text="Proceed",
                                   font=(FONT[0], FONT[1]+2, "bold"),
                                   bg=SOFT_YELLOW,
                                   fg=DARK_TEXT,
                                   bd=0,
                                   padx=20,
                                   pady=10,
                                   activebackground=SOFT_YELLOW,
                                   command=lambda: controller.next_frame("Guidelines"))
        proceed_button.pack(pady=15)
