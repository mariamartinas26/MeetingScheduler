import tkinter as tk


class MenuPage:
    """
    Main menu page of the application
    """

    def __init__(self, parent, show_person, exit_app):
        self.frame = tk.Frame(parent)

        tk.Label(
            self.frame,
            text="Meeting Scheduler",
            font=("Arial", 18, "bold")
        ).pack(pady=30)

        tk.Button(
            self.frame,
            text="Add Person",
            width=25,
            height=2,
            command=show_person,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)

        tk.Button(
            self.frame,
            text="Exit",
            width=25,
            height=2,
            command=exit_app,
            bg="#f44336",
            fg="white"
        ).pack(pady=30)


    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
