import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
from db import get_all_img_names, get_user_img_names, get_filtered_img_names

class PokebookApp:
    def __init__(self, root, username, user_id):
        self.root = root
        self.username = username
        self.user_id = user_id
        self.columns = 4

        self.root.title(f"Pokébook – {username}")

        # Fenstergröße und Position neu setzen
        window_width = 1465
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Grid-Konfiguration zurücksetzen
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.all_img_paths = self.get_all_img_paths()
        self.user_img_paths = self.get_user_img_paths()
        self.only_user_cards = False
        self.setup_ui()
        
        # alle Karten beim öffnen anzeigen
        self.show_all_cards()
        self.all_cards_button.configure(bootstyle="secondary")

    def get_all_img_paths(self):
        base_path = os.getenv("PATH_ALL_CARDS")
        all_img_names = get_all_img_names()
        return [os.path.join(base_path, name) for name in all_img_names]

    def get_user_img_paths(self):
        base_path = os.getenv("PATH_ALL_CARDS")
        user_img_names = get_user_img_names(self.user_id)
        return [os.path.join(base_path, name) for name in user_img_names]
    
    def change_button_colour(self, clicked_button, other_button):
        clicked_button.configure(bootstyle="secondary")
        other_button.configure(bootstyle="secondary.Outline.TButton")

    def show_all_cards(self):
        self.clear_grid()
        self.only_user_cards = False
        for index, path in enumerate(self.all_img_paths):
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
    
    def show_user_cards(self):
        self.clear_grid()
        self.only_user_cards = True
        for index, path in enumerate(self.user_img_paths):
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
    
    def filter_cards(self, only_user_cards=False):
        typ = self.type_combobox.get()
        rarity = self.rarity_combobox.get()
        pack = self.pack_combobox.get()

        # Mapping von Namen zu Index
        typ = self.type_map.get(typ) if typ else None
        rarity = self.rarity_map.get(rarity) if rarity else None
        pack = self.pack_map.get(pack) if pack else None

        if only_user_cards:
            img_names = get_filtered_img_names(user_id=self.user_id, typ=typ, rarity=rarity, pack=pack, only_user_cards=True)
        else:
            img_names = get_filtered_img_names(typ=typ, rarity=rarity, pack=pack, only_user_cards=False)
        base_path = os.getenv("PATH_ALL_CARDS")
        filtered_paths = [os.path.join(base_path, name) for name in img_names]

        self.clear_grid()
        self.card_images = []
        for index, path in enumerate(filtered_paths):
            try:
                img = Image.open(path)
                img = img.resize((276, 390))
                photo = ImageTk.PhotoImage(img)
                self.card_images.append(photo)
                label = ttk.Label(self.scrollable_frame, image=photo)
                label.image = photo
                row = index // self.columns
                col = index % self.columns
                label.grid(row=row, column=col, padx=5, pady=5)
            except Exception as e:
                print(f"Fehler bei {path}: {e}")

    def reset_button(self):
        self.type_combobox.set("")
        self.rarity_combobox.set("")
        self.pack_combobox.set("")
        
        self.name_entry.delete(0, tk.END)

        if self.only_user_cards:
            self.show_user_cards()
        else:
            self.show_all_cards()

    def search_by_name(self):
        name = self.name_entry.get().strip()
        if not name:
            return 
        if self.only_user_cards:
            img_names = get_filtered_img_names(user_id=self.user_id, typ=None, rarity=None, pack=None, only_user_cards=True)
        else:
            img_names = get_filtered_img_names(typ=None, rarity=None, pack=None, only_user_cards=False)

        img_names = [n for n in img_names if name in n.lower()]
        base_path = os.getenv("PATH_ALL_CARDS")
        filtered_paths = [os.path.join(base_path, n) for n in img_names]

        self.clear_grid()
        self.card_images = []
        for index, path in enumerate(filtered_paths):
            try:
                img = Image.open(path)
                img = img.resize((276, 390))
                photo = ImageTk.PhotoImage(img)
                self.card_images.append(photo)
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
            command=lambda:[self.show_user_cards(), self.change_button_colour(self.my_cards_button, self.all_cards_button)])
        self.my_cards_button.grid(row=0, column=1)

        # Suche 
        self.search_label = ttk.Label(self.menu_frame, text="Suche nach Namen:", bootstyle="secondary", font=("Helvetica bold", 14))
        self.search_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(20,8))

        self.name_entry = ttk.Entry(self.menu_frame, bootstyle="secondary")
        self.name_entry.grid(row=2, column=0, columnspan=2, sticky="nsw")

        self.search_button = ttk.Button(self.menu_frame, text="OK", bootstyle="secondary", command=self.search_by_name)
        self.search_button.grid(row=2, column=1, sticky="e")

        # Filter
        self.filter_label = ttk.Label(self.menu_frame, text="Filter:", bootstyle="secondary", font=("Helvetica bold", 14))
        self.filter_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(20,10))

        # Typ Combobox
        self.type_label = ttk.Label(self.menu_frame, text="Typ:", bootstyle="secondary", font=("Helvetica", 14))
        self.type_label.grid(row=4, column=0, columnspan=2, sticky="w")
        self.type_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["","Pflanze", "Feuer", "Wasser", "Elektro", "Psycho", "Kampf", "Finsternis", "Metall", "Fee", "Drache", "Farblos"])
        self.type_combobox.grid(row=5, column=0, columnspan=2, pady=(5,10))
        self.type_map = {"Pflanze": 1, "Feuer": 2, "Wasser": 3, "Elektro": 4, "Psycho": 5, "Kampf": 6, "Finsternis": 7, "Metall": 8, "Fee": 9, "Drache": 10, "Farblos": 11}

        # Seltenheit Combobox
        self.rarity_label = ttk.Label(self.menu_frame, text="Seltenheit:", bootstyle="secondary", font=("Helvetica", 14))
        self.rarity_label.grid(row=6, column=0, columnspan=2, sticky="w")
        self.rarity_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Common", "Uncommon", "Rare", "Double Rare", "Ultra Rare", "Art Rare", "Special Art Rare", "Secret Rare"])
        self.rarity_combobox.grid(row=7, column=0, columnspan=2, pady=(5,10))
        self.rarity_map = {"Common": 1, "Uncommon": 2, "Rare": 3, "Double Rare": 4, "Ultra Rare": 5, "Art Rare": 6, "Special Art Rare": 7, "Secret Rare": 8}

        # Päckchen Combobox
        self.pack_label = ttk.Label(self.menu_frame, text="Päckchen:",bootstyle="secondary", font=("Helvetica", 14))
        self.pack_label.grid(row=8, column=0, columnspan=2, sticky="w")
        self.pack_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Sonnen & Mond Zyklus", "Karmesin & Purpur Zyklus"])
        self.pack_combobox.grid(row=9, column=0, columnspan=2, pady=(5,10))
        self.pack_map = {"Sonnen & Mond Zyklus": 1, "Karmesin & Purpur Zyklus": 2}

        # Filtern Button
        self.filter_button = ttk.Button(self.menu_frame, text="Filtern", bootstyle="secondary", width=8, command=lambda: self.filter_cards(only_user_cards = self.only_user_cards))
        self.filter_button.grid(row=10, column=0, padx=5, pady=10, sticky="e")

        # Reset Button
        self.reset_button = ttk.Button(self.menu_frame, text="Reset", width=8, bootstyle="secondary", command=self.reset_button)
        self.reset_button.grid(row=10, column=1, padx=5, pady=10, sticky="w")

        # Grid Frame 
        self.grid_frame = ttk.Frame(self.root)
        self.grid_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        # Container für Canvas
        self.container = ttk.Frame(self.root)
        self.container.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

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
PokebookApp(root, "1", 1)
root.mainloop()
