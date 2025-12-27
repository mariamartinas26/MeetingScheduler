import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class MeetingForm:
    """
    gui for scheduling meetings
    """

    def __init__(self,parent,db,show_menu):
        self.db=db
        self.show_menu=show_menu
        self.frame=tk.Frame(parent)

        tk.Button(
            self.frame,
            text="Back to Menu",
            command=self.show_menu
        ).pack(anchor="w",pady=5)

        tk.Label(
            self.frame,
            text="Schedule Meeting",
            font=("Poppins", 14, "bold")
        ).pack(pady=10)

        self._entry("Title")
        self.title_entry=self.last_entry

        self._entry("Description")
        self.desc_entry = self.last_entry

        self._entry("Location")
        self.location_entry = self.last_entry

        self._entry("Start (DD-MM-YYYY HH:MM)")
        self.start_entry = self.last_entry

        self._entry("End (DD-MM-YYYY HH:MM)")
        self.end_entry = self.last_entry

        tk.Label(self.frame, text="Participants").pack(anchor="w")
        self.participants = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, width=40)
        self.participants.pack()

        self.person_map = {}
        for pid, name in self.db.get_all_persons():
            self.person_map[name] = pid
            self.participants.insert(tk.END, name)

        tk.Button(
            self.frame,
            text="Schedule Meeting",
            command=self.submit,
            bg="#2196F3",
            fg="white",
            width=20
        ).pack(pady=15)

    def _entry(self, label):
        tk.Label(self.frame, text=label).pack(anchor="w")
        e = tk.Entry(self.frame, width=40)
        e.pack(pady=3)
        self.last_entry = e

    def show(self):
        """show form"""
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide(self):
        """hide form"""
        self.frame.pack_forget()

    def submit(self):
        """
        Validates input and schedules a meeting
        """

        try:
            start=datetime.strptime(
                self.start_entry.get(),
                "%d-%m-%Y %H:%M"
            )
            end = datetime.strptime(
                self.end_entry.get(),
                "%d-%m-%Y %H:%M"
            )
        except ValueError:
            messagebox.showerror(
                "Error",
            "Invalid date format. Use DD-MM-YYYY HH:MM"
            )
            return

        now = datetime.now()

        if start<now:
            messagebox.showerror(
                "Error",
                "Start time cannot be in the past"
            )
            return

        if end <= start:
            messagebox.showerror(
                "Error",
                "End time must be after start time"
            )
            return

        #validate participants
        selected = self.participants.curselection()
        if not selected:
            messagebox.showerror(
                "Error",
            "At least one participant must be selected"
            )
            return

        participant_ids = [
            self.person_map[self.participants.get(i)]
            for i in selected
        ]

        success, message = self.db.add_meeting(
            self.title_entry.get().strip(),
            self.desc_entry.get().strip(),
            start,
            end,
            self.location_entry.get().strip(),
            participant_ids
        )

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

