import tkinter as tk
from tkinter import messagebox

from database import DatabaseManager
from config.db_config import DEFAULT_CONFIG
from gui.menu_page import MenuPage
from gui.person_form import PersonForm


def main():
    #connect to database
    db = DatabaseManager()
    success, message = db.connect(**DEFAULT_CONFIG)

    if not success:
        messagebox.showerror("Database Error", message)
        return

    root = tk.Tk()
    root.title("Meeting Scheduler")
    root.geometry("500x400")

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    menu_page = None
    person_form = None

    def show_menu():
        person_form.hide()
        menu_page.show()

    def show_person():
        menu_page.hide()
        person_form.show()

    #pages
    person_form = PersonForm(container, db, show_menu)
    menu_page = MenuPage(
        container,
        show_person=show_person,
        exit_app=root.destroy
    )

    show_menu()

    root.mainloop()


if __name__ == "__main__":
    main()
