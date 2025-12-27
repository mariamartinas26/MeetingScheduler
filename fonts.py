import tkinter as tk
from tkinter import font

def get_poppins(size=12, weight="normal"):
    """
    Returns font Poppins is exists
    """
    root = tk._default_root
    if not root:
        root = tk.Tk()
        root.withdraw()

    available_fonts = font.families()

    if "Poppins" in available_fonts:
        return ("Poppins", size, weight)

    #fallback
    return ("Arial", size, weight)
