import tkinter as tk
from tkinter import messagebox

from config.db_config import DEFAULT_CONFIG
from database import DatabaseManager
from gui.meeting_form import MeetingForm
from gui.menu_page import MenuPage
from gui.person_form import PersonForm
from gui.view_meetings_page import ViewMeetingsPage


def main():
    """
    Entry point of the application

    The application uses a single container frame and switches
    between pages by showing/hiding frames

    Returns:
        None
    """
    #connect to database
    db = DatabaseManager()
    success, message = db.connect(**DEFAULT_CONFIG)

    if not success:
        messagebox.showerror("Database Error", message)
        return
    else:
        print("Database connection established")

    #initialize main app window
    root = tk.Tk()
    root.title("Meeting Scheduler")
    root.geometry("500x800")

    #container for all pages
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    menu_page = None
    person_form = None
    meeting_form = None
    view_meetings_page = None

    #function to hide all pages
    def hide_all_pages():
        """
        Hide all app pages
        Helper function which ensures that only one page
        is visible at a time

        Returns:
            None
        """
        if menu_page:
            menu_page.hide()
        if person_form:
            person_form.hide()
        if meeting_form:
            meeting_form.hide()
        if view_meetings_page:
            view_meetings_page.hide()

    def show_menu():
        """
        Display menu page

        Returns:
            None
        """
        hide_all_pages()
        menu_page.show()

    def show_person():
        """
        Display person page

        Returns:
            None
        """
        hide_all_pages()
        person_form.show()

    def show_meeting():
        """
        Display meeting page

        Returns:
            None
        """
        hide_all_pages()
        meeting_form.show()

    def show_view_meetings_interval():
        """
        Display view meetings interval page

        Returns:
            None
        """
        hide_all_pages()
        view_meetings_page.show()

    #initialize pages
    person_form = PersonForm(container, db, show_menu)
    meeting_form= MeetingForm(container, db, show_menu)
    view_meetings_page = ViewMeetingsPage(container, db, show_menu)

    menu_page = MenuPage(
        container,
        show_person=show_person,
        show_meeting=show_meeting,
        show_view_meetings_interval=show_view_meetings_interval,
        exit_app=root.destroy
    )

    #show main menu initially
    show_menu()
    root.mainloop()


if __name__ == "__main__":
    main()
