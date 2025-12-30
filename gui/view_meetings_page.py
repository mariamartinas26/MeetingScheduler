import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from fonts import get_poppins

class ViewMeetingsPage:
    """
    GUI for displaying meetings in an interval
    """

    def __init__(self, parent, db,show_menu):
        self.db=db
        self.show_menu=show_menu
        self.frame=tk.Frame(parent)
        self.font_regular = get_poppins(size=11)
        self.font_bold = get_poppins(size=13, weight="bold")

        style = ttk.Style()
        style.configure(
            "Poppins.Treeview",
            font=self.font_regular,
            rowheight=26
        )

        style.configure(
            "Poppins.Treeview.Heading",
            font=self.font_bold
        )

        tk.Button(
            self.frame,
            text="Back to Menu",
            font=self.font_regular,
            command=self.show_menu
        ).pack(anchor="w",pady=5)

        tk.Label(
            self.frame,
            text="View Meetings",
            font=self.font_bold
        ).pack(pady=10)

        #interval
        tk.Label(
            self.frame,
            text="Start (DD-MM-YYYY HH:MM)",
            font=self.font_regular
        ).pack(anchor="w")

        self.start_entry = tk.Entry(
            self.frame,
            width=40,
            font=self.font_regular
        )
        self.start_entry.pack(pady=3)

        tk.Label(
            self.frame,
            text="End (DD-MM-YYYY HH:MM)",
            font=self.font_regular
        ).pack(anchor="w")

        self.end_entry = tk.Entry(
            self.frame,
            width=40,
            font=self.font_regular
        )
        self.end_entry.pack(pady=3)

        tk.Button(
            self.frame,
            text="Search",
            command=self.search,
            font=self.font_regular,
            width=20
        ).pack(pady=10)

        #table for showing details about meetings in interval
        columns = ("title","description", "start", "end", "location", "participants")
        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            style="Poppins.Treeview"
        )

        self.tree.heading("title", text="Title")
        self.tree.heading("description", text="Description")
        self.tree.heading("start", text="Start")
        self.tree.heading("end", text="End")
        self.tree.heading("location", text="Location")
        self.tree.heading("participants", text="Participants")

        self.tree.pack(fill="both", expand=True, pady=10)

    def show(self):
        """
        Show view meetings page
        """
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide(self):
        """
        Hide view meetings page
        """
        self.frame.pack_forget()

    def search(self):
        """
        Search meetings in a given interval function
        """
        #clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            start=datetime.strptime(self.start_entry.get(), "%d-%m-%Y %H:%M")
            end=datetime.strptime(self.end_entry.get(), "%d-%m-%Y %H:%M")
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid format for date. Use DD-MM-YYYY HH:MM"
            )
            return

        if end<=start:
            messagebox.showerror(
                "Error",
                "End time must be after start time"
            )
            return

        meetings=self.db.get_meetings_in_interval(start, end)

        if not meetings:
            messagebox.showerror(
                "No results",
                "No meetings found in this interval"
            )
            return

        for title, description, start_t, end_t, location , participants in meetings:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    title,
                    description,
                    start_t,
                    end_t,
                    location,
                    participants
                )
            )