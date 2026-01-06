import tkinter as tk

from fonts import FONT_NORMAL, FONT_TITLE


class MenuPage:
    """
    Main menu page of the application
    """

    def __init__(self, parent, show_person, show_meeting,show_view_meetings_interval, exit_app):
        self.frame = tk.Frame(parent)

        #title
        tk.Label(
            self.frame,
            text="Meeting Scheduler",
            font=FONT_TITLE,
        ).pack(pady=30)

        #add person button
        tk.Button(
            self.frame,
            text="Add Person",
            width=25,
            height=2,
            command=show_person,
            font=FONT_NORMAL,
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
            font=FONT_NORMAL,
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
            font=FONT_NORMAL,
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
            font=FONT_NORMAL,
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
