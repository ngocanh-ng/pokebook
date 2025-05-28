import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
from db import get_all_img_names

class PokeBookApp:
    def __init__(self, root, username, user_id):
        self.root = root
        self.username = username
        self.user_id = user_id
        self.columns = 4

        self.root.title(f"Pokébook – {username}")
        self.root.geometry("1465x900")

        self.img_paths = self.get_img_paths()
        self.setup_ui()
        
        # alle Karten beim öffnen anzeigen
        self.show_all_cards()
        self.all_cards_button.configure(bootstyle="secondary")

    def get_img_paths(self):
        base_path = os.getenv("PATH_ANH")
        img_names = get_all_img_names()
        return [os.path.join(base_path, name) for name in img_names] 
    
    def change_button_colour(self, clicked_button, other_button):
        clicked_button.configure(bootstyle="secondary")
        other_button.configure(bootstyle="secondary.Outline.TButton")

    def show_all_cards(self,):
        self.clear_grid()
        for index, path in enumerate(self.img_paths):
            try:
                img = Image.open(path)
                img = img.resize((276, 390))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(self.scrollable_frame, image=photo)
                label.image = photo
                row = index // self.columns
                col = index % self.columns
                label.grid(row=row, column=col, padx=5, pady=5)
            except Exception as e:
                print(f"Fehler bei {path}: {e}")

    def clear_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def setup_ui(self):
        # Menü-Frame
        self.menu_frame = ttk.Frame(self.root, borderwidth=10, relief = tk.GROOVE)
        self.menu_frame.grid(row=0, column=0, sticky="n", padx=(15,5))

        # Alle Karten Button
        self.all_cards_button = ttk.Button(
            self.menu_frame, 
            text="Alle Karten", 
            bootstyle="secondary.Outline.TButton", 
            width=10, 
            command=lambda:[self.show_all_cards(), self.change_button_colour(self.all_cards_button, self.my_cards_button)])
        self.all_cards_button.grid(row=0, column=0)

        # Meine Karten Button
        self.my_cards_button = ttk.Button(
            self.menu_frame, 
            text="Meine Karten", 
            bootstyle="secondary.Outline.TButton", 
            width=10,
            command=lambda:[self.change_button_colour(self.my_cards_button, self.all_cards_button)])
        self.my_cards_button.grid(row=0, column=1)

        # Suche 
        self.search_label = ttk.Label(self.menu_frame, text="Suche nach Namen:", bootstyle="secondary", font=("Helvetica bold", 14))
        self.search_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(20,8))

        self.name_entry = ttk.Entry(self.menu_frame, bootstyle="secondary")
        self.name_entry.grid(row=2, column=0, columnspan=2, sticky="nsw")

        self.search_button = ttk.Button(self.menu_frame, text="OK", bootstyle="secondary")
        self.search_button.grid(row=2, column=1, sticky="e")

        # Filter
        self.filter_label = ttk.Label(self.menu_frame, text="Filter:", bootstyle="secondary", font=("Helvetica bold", 14))
        self.filter_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(20,10))

        # Typ Combobox
        self.type_label = ttk.Label(self.menu_frame, text="Typ:", bootstyle="secondary", font=("Helvetica", 14))
        self.type_label.grid(row=4, column=0, columnspan=2, sticky="w")
        self.type_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["Feuer", "Wasser", "Pflanze", "Elektro", "Psycho", "Kampf", "Finsternis", "Metall", "Fee", "Drache", "Farblos"])
        self.type_combobox.grid(row=5, column=0, columnspan=2, pady=(5,10))

        # Seltenheit Combobox
        self.rarity_label = ttk.Label(self.menu_frame, text="Seltenheit:", bootstyle="secondary", font=("Helvetica", 14))
        self.rarity_label.grid(row=6, column=0, columnspan=2, sticky="w")
        self.rarity_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["Common", "Uncommon", "Rare", "Double Rare", "Ultra Rare", "Art Rare", "Special Art Rare", "Secret Rare"])
        self.rarity_combobox.grid(row=7, column=0, columnspan=2, pady=(5,10))

        # Serie Combobox
        self.set_label = ttk.Label(self.menu_frame, text="Serie:",bootstyle="secondary", font=("Helvetica", 14))
        self.set_label.grid(row=8, column=0, columnspan=2, sticky="w")
        self.set_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["Sonnen & Mond Zyklus", "Karmesin & Purpur Zyklus"])
        self.set_combobox.grid(row=9, column=0, columnspan=2, pady=(5,10))

        # Filtern Button
        self.filter_button = ttk.Button(self.menu_frame, text="Filtern", bootstyle="secondary")
        self.filter_button.grid(row=10, column=0, columnspan=2, pady=10)

        # Grid Frame 
        self.grid_frame = ttk.Frame(self.root)
        self.grid_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        # Grid Frame ausdehnen
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        # Canvas für Scrollbar
        self.canvas = tk.Canvas(self.container)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Scrollable Frame 
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))) # Aktualisiert den Scrollbereich des Canvas, wenn sich der Inhalt von scrollable_frame ändert.

        # Scrollable Frame oben links im Canvas platzieren
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Alle Spalten im scrollable_frame gleichmäßig verteilen
        self.scrollable_frame.columnconfigure(tuple(range(self.columns)), weight=1)

# Test
root = ttk.Window(themename="minty")
PokeBookApp(root, "1", 1)
root.mainloop()

