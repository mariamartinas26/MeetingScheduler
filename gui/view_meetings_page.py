import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from fonts import FONT_NORMAL, FONT_TITLE


class ViewMeetingsPage:
    """
    GUI for viewing, exporting and importing meetings

    This page allows the user to:
        - Search meetings in the db within a given time interval
        - Display meetings
        - Export selected meetings to .ics file
        - Import meetings from .ics file into db
    """

    def __init__(self, parent, db,show_menu):
        """
        Initializes the page

        Returns:
            None
        """
        self.db=db
        self.show_menu=show_menu
        self.frame=tk.Frame(parent)

        style = ttk.Style()
        style.configure(
            "Poppins.Treeview",
            font=FONT_NORMAL,
            rowheight=26
        )

        style.configure(
            "Poppins.Treeview.Heading",
            font=FONT_NORMAL
        )

        #Back button
        tk.Button(
            self.frame,
            text="Back",
            font=FONT_NORMAL,
            command=self.show_menu
        ).pack(anchor="w",pady=5)

        #Page Title
        tk.Label(
            self.frame,
            text="View Meetings",
            font=FONT_TITLE
        ).pack(pady=10)

        #start interval input
        tk.Label(
            self.frame,
            text="Start (DD-MM-YYYY HH:MM)",
            font=FONT_NORMAL
        ).pack(anchor="w")

        self.start_entry = tk.Entry(
            self.frame,
            width=40,
            font=FONT_NORMAL
        )
        self.start_entry.pack(pady=3)

        #end interval input
        tk.Label(
            self.frame,
            text="End (DD-MM-YYYY HH:MM)",
            font=FONT_NORMAL
        ).pack(anchor="w")

        self.end_entry = tk.Entry(
            self.frame,
            width=40,
            font=FONT_NORMAL
        )
        self.end_entry.pack(pady=3)

        #search button
        tk.Button(
            self.frame,
            text="Search",
            command=self.search,
            font=FONT_NORMAL,
            width=20
        ).pack(pady=10)

        #export meetings button
        tk.Button(
            self.frame,
            text="Export meetings",
            command=self.export_meetings,
            font=FONT_NORMAL,
            width=25
        ).pack(pady=5)

        #import meetings button
        tk.Button(
            self.frame,
            text="Import meetings",
            command=self.import_meetings,
            font=FONT_NORMAL,
            width=25
        ).pack(pady=5)

        #table used to display meetings
        columns = ("title","description", "start", "end", "location", "participants")
        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            style="Poppins.Treeview",
            selectmode="extended" #for selecting multiple meetings
        )

        #headings
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

        Returns:
            None
        """
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide(self):
        """
        Hide view meetings page

        Returns:
            None
        """
        self.frame.pack_forget()

    def search(self):
        """
        Search meetings in a given interval function and display them in the table

        Steps:
            -Clears current Treeview rows
            -Parses and validates start/end datetime format (DD-MM-YYYY HH:MM)
            -Ensures end > start
            -Calls db.get_meetings_in_interval(start, end)
            -Displays meetings in the Treeview

        Returns:
            None
        """
        #clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            #convert text to datetime object
            start=datetime.strptime(self.start_entry.get(), "%d-%m-%Y %H:%M")
            end=datetime.strptime(self.end_entry.get(), "%d-%m-%Y %H:%M")
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid format for date. Use DD-MM-YYYY HH:MM"
            )
            return

        #validate interval order
        if end<=start:
            messagebox.showerror(
                "Error",
                "End time must be after start time"
            )
            return

        #get meetings from db
        ok,meetings=self.db.get_meetings_in_interval(start, end)
        if not ok:
            messagebox.showerror("Error", meetings)
            return

        #handle empty results
        if not meetings:
            messagebox.showerror(
                "No results",
                "No meetings found in this interval"
            )
            return

        #insert rows into table
        for title, description, start_t, end_t, location , participants in meetings:
            #transform from datetime to string
            start_str = start_t.strftime("%d-%m-%Y %H:%M")
            end_str = end_t.strftime("%d-%m-%Y %H:%M")
            self.tree.insert(
                "",
                tk.END,
                values=(title, description, start_str, end_str, location, participants)
            )


    def export_meetings(self):
        """
        Export selected meetings from the table to .ics file

        Steps:
            -Check if any meetings are selected in the Treeview
            -Ask user for a save location
            -Convert selected table rows into meeting tuples
            -Call db.export_meetings_to_file(meetings_to_export, file_path)
            -Display success/error feedback message

        Returns:
            None
        """

        selected_items=self.tree.selection()

        if not selected_items:
            messagebox.showerror(
                "Error",
                "No selected meetings to export"
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Save meetings",
            defaultextension=".ics",
            filetypes=[("iCalendar files", "*.ics")],
            initialfile=f"meetings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        )

        if not file_path:
            return  #stopped saving

        meetings_to_export=[]
        for item_id in selected_items:
            values=self.tree.item(item_id, "values")

            title=values[0]
            description = values[1]
            start_dt = datetime.strptime(values[2], "%d-%m-%Y %H:%M")
            end_dt = datetime.strptime(values[3], "%d-%m-%Y %H:%M")
            location = values[4]
            participants = values[5]

            meetings_to_export.append((title, description, start_dt, end_dt, location, participants))

        success,message=self.db.export_meetings_to_file(meetings_to_export,file_path)

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def import_meetings(self):
        """
        import meetings from ics file into the db

        Steps:
            -Ask user to select an ICS file
            -Call db.import_meetings_from_file(file_path)
            -Display success/error message

        Returns:
            None
        """
        file_path = filedialog.askopenfilename(
            title="Import meetings",
            filetypes=[("iCalendar files", "*.ics")]
        )

        if not file_path:
            return #stopped saving

        success, message = self.db.import_meetings_from_file(file_path)

        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Import error", message)



