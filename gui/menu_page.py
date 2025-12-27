import tkinter as tk
from fonts import get_poppins

class MenuPage:
    """
    Main menu page of the application
    """

    def __init__(self, parent, show_person, show_meeting, exit_app):
        self.frame = tk.Frame(parent)

        #title
        tk.Label(
            self.frame,
            text="Meeting Scheduler",
            font=("Poppins", 18, "bold")
        ).pack(pady=30)

        #add person button
        tk.Button(
            self.frame,
            text="Add Person",
            width=25,
            height=2,
            command=show_person,
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
            bg="#2196F3",
            fg="white"
        ).pack(pady=10)

        #exit button
        tk.Button(
            self.frame,
            text="Exit",
            width=25,
            height=2,
            command=exit_app,
            bg="#f44336",
            fg="white"
        ).pack(pady=10)


    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
