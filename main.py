import tkinter as tk
import ttkbootstrap as ttk # Theme extension
import os
from db import get_all_img_names
from PIL import Image, ImageTk # Pillow = Bildverarbeitungsbibliothek
from dotenv import load_dotenv

load_dotenv()

# functions
def get_img_paths():
    base_path = os.getenv("BASE_PATH_MAC")
    img_names = get_all_img_names()
    return [os.path.join(base_path, name) for name in img_names] 

def change_button_colour(clicked_button, other_button):
    clicked_button.configure(bootstyle="secondary")
    other_button.configure(bootstyle="secondary.Outline.TButton")

def show_all_cards():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    for index, path in enumerate(img_paths):
        try:
            img = Image.open(path)
            img = img.resize((276, 390))
            photo = ImageTk.PhotoImage(img)

            label = ttk.Label(scrollable_frame, image=photo)
            label.image = photo
            row = index // columns
            col = index % columns
            label.grid(row=row, column=col, padx=5, pady=5)
        except Exception as e:
            print(f"Fehler bei {path}: {e}")

def show_my_cards():
    return
    
# Window
root = ttk.Window(themename="minty")
root.title("Pokébook")
root.geometry("1465x900")

# Menu
menu_frame = ttk.Frame(root, borderwidth=10, relief = tk.GROOVE)
menu_frame.grid(row=0, column=0, sticky="n", padx=(15,5))

# Buttons
all_cards_button = ttk.Button(
    menu_frame, 
    text="Alle Karten", 
    bootstyle="secondary.Outline.TButton", 
    width=10, 
    command=lambda:[show_all_cards(), change_button_colour(all_cards_button, my_cards_button)])
all_cards_button.pack(side="left")

my_cards_button = ttk.Button(
    menu_frame, 
    text="Meine Karten", 
    bootstyle="secondary.Outline.TButton", 
    width=10,
    command=lambda:[show_my_cards(), change_button_colour(my_cards_button, all_cards_button)])
my_cards_button.pack(side="right")

# Container frame for canvas and scrollbar
container = ttk.Frame(root)
container.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

# Make the container expand
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=1)

# Canvas
canvas = tk.Canvas(container)
canvas.grid(row=0, column=0, sticky="nsew")

# Scrollbar
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
canvas.configure(yscrollcommand=scrollbar.set)

# Scrollable frame inside the canvas
scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Create a window inside the canvas to hold the frame
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Konfiguration
columns = 4
scrollable_frame.columnconfigure(tuple(range(columns)), weight=1)
img_paths = get_img_paths()

# show all cards when app is opened
all_cards_button.configure(bootstyle="secondary")
show_all_cards()

# run
root.mainloop()