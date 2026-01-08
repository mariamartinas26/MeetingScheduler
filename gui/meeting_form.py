import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from fonts import FONT_NORMAL, FONT_TITLE


class MeetingForm:
    """
    GUI for scheduling meetings

    This form allows the user to:
        - enter meeting title/description/location
        - set start and end datetime
        - select participants from existing persons in the database
        - submit the meeting to be stored in the db
    """

    def __init__(self,parent,db,show_menu):
        """
        Initialize the meeting form

        Returns:
            None
        """
        self.db=db
        self.show_menu=show_menu
        self.frame=tk.Frame(parent)

        #Back button
        tk.Button(
            self.frame,
            text="Back",
            command=self.show_menu,
            font=FONT_NORMAL,
        ).pack(anchor="w",pady=5)

        #Page title
        tk.Label(
            self.frame,
            text="Schedule Meeting",
            font=FONT_TITLE,
        ).pack(pady=10)

        #Title input
        tk.Label(self.frame, text="Title", font=FONT_NORMAL).pack(anchor="w")
        self.title_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.title_entry.pack(pady=5)

        #Description input
        tk.Label(self.frame, text="Description", font=FONT_NORMAL).pack(anchor="w")
        self.desc_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.desc_entry.pack(pady=5)

        #Location input
        tk.Label(self.frame, text="Location", font=FONT_NORMAL).pack(anchor="w")
        self.location_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.location_entry.pack(pady=5)

        #Start input
        tk.Label(self.frame, text="Start (DD-MM-YYYY HH:MM)", font=FONT_NORMAL).pack(anchor="w")
        self.start_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.start_entry.pack(pady=5)

        #End input
        tk.Label(self.frame, text="End (DD-MM-YYYY HH:MM)", font=FONT_NORMAL).pack(anchor="w")
        self.end_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.end_entry.pack(pady=5)

        # A mapping form name -> person_id
        self.person_map = {}

        #Participants list
        tk.Label(self.frame, text="Participants", font=FONT_NORMAL).pack(anchor="w")
        self.participants = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, width=40, height=7,font=FONT_NORMAL)
        self.participants.pack(pady=5)

        #Submit button
        tk.Button(
            self.frame,
            text="Schedule Meeting",
            command=self.submit,
            bg="#2196F3",
            fg="white",
            font=FONT_NORMAL,
            width=20
        ).pack(pady=15)


    def load_persons(self):
        self.participants.delete(0, tk.END)
        self.person_map = {}

        ok,persons=self.db.get_all_persons()
        if not ok:
            messagebox.showerror("Error", persons)
            return

        for pid,name in persons:
            self.person_map[name] = pid
            self.participants.insert(tk.END, name)

    def show(self):
        """
        Display the meeting form and refresh the list of persons

        Returns:
            None
        """
        self.load_persons() #refresh persons list
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide(self):
        """
        Hide the meeting form

        Returns:
            None
        """
        self.frame.pack_forget()

    def submit(self):
        """
        Validates input and schedules a meeting

        After validation, the method:
            - Converts selected participant names to participant_ids
            - Calls db.add_meeting(...)
            - Displays success or error feedback message

        Returns:
            None
        """

        #datetime inputs
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

        #validate participants selection
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

        #submit meeting to db_manager
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

