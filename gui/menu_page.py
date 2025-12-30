import tkinter as tk
from fonts import get_poppins

class MenuPage:
    """
    Main menu page of the application
    """

    def __init__(self, parent, show_person, show_meeting,show_view_meetings_interval, exit_app):
        self.frame = tk.Frame(parent)
        self.font_title = get_poppins(size=18, weight="bold")
        self.font_button = get_poppins(size=10)

        #title
        tk.Label(
            self.frame,
            text="Meeting Scheduler",
            font=self.font_title
        ).pack(pady=30)

        #add person button
        tk.Button(
            self.frame,
            text="Add Person",
            width=25,
            height=2,
            command=show_person,
            font=self.font_button,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)

        #schedule meeting button
        tk.Button(
            self.frame,
            text="Schedule Meeting",
            width=25,
            height=2,
            command=show_meeting,
            font=self.font_button,
            bg="#2196F3",
            fg="white"
        ).pack(pady=10)

        #view meetings in interval
        tk.Button(
            self.frame,
            text="View Meetings",
            width=25,
            height=2,
            command=show_view_meetings_interval,
            font=self.font_button,
            bg="#9C27B0",
            fg="white"
        ).pack(pady=10)

        #exit button
        tk.Button(
            self.frame,
            text="Exit",
            width=25,
            height=2,
            command=exit_app,
            font=self.font_button,
            bg="#f44336",
            fg="white"
        ).pack(pady=10)


    def show(self):
        """
        Show menu page
        """
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        """
        Hide menu page
        """
        self.frame.pack_forget()
