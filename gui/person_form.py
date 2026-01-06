import tkinter as tk
from tkinter import messagebox

from fonts import FONT_NORMAL, FONT_TITLE


class PersonForm:
    """
    Form for adding a new person into the database
    This class provides a Tkinter user interface that allows the user
    to input personal information (name, email, phone) and submit it to the
    database through the DatabaseManager
    """

    def __init__(self, parent, db_manager,show_menu):
        """
        Initialize the person form

        Returns:
            None
        """
        self.db = db_manager
        self.show_menu = show_menu
        self.frame = tk.Frame(parent)

        #back to menu button
        tk.Button(
            self.frame,
            text="Back",
            font=FONT_NORMAL,
            command=self.show_menu
        ).pack(anchor="w", pady=5)

        #add new person button
        tk.Label(
            self.frame,
            text="Add New Person",
            font=FONT_TITLE,
        ).pack(pady=10)

        #Name input
        tk.Label(self.frame, text="Name",font=FONT_NORMAL).pack(anchor="w")
        self.name_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.name_entry.pack(pady=5)

        #Email input
        tk.Label(self.frame, text="Email",font=FONT_NORMAL).pack(anchor="w")
        self.email_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.email_entry.pack(pady=5)

        #Phone input
        tk.Label(self.frame, text="Phone",font=FONT_NORMAL).pack(anchor="w")
        self.phone_entry = tk.Entry(self.frame, width=40, font=FONT_NORMAL)
        self.phone_entry.pack(pady=5)

        #Submit button
        tk.Button(
            self.frame,
            text="Add Person",
            command=self.submit,
            bg="#4CAF50",
            fg="white",
            font=FONT_NORMAL,
            width=20
        ).pack(pady=15)

    def show(self):
        """
        Display the person form

        Returns:
            None
        """
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide(self):
        """
        Hide the person form

        Returns:
            None
        """
        self.frame.pack_forget()

    def submit(self):
        """
        Handles form submission

        Collects user input from the entry fields, sends the data to the
        database using DatabaseManager.add_person(), and displays a success
        or error message

        Returns:
            None
        """
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()

        success, message = self.db.add_person(name, email, phone)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)

    def clear_fields(self):
        """
        Clear all input fields in the form

        Returns:
            None
        """
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
