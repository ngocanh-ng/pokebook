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

        # Fenstergröße und Position
        WINDOW_WIDTH = 1465
        WINDOW_HEIGHT = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Grid-Konfiguration zurücksetzen
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Pfade für Bilder 
        self.all_img_paths = self.get_all_img_paths()
        self.user_img_paths = self.get_user_img_paths()
        
        self.only_user_cards = False
        self.name_filter_after_id = None

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

    def display_images(self, image_paths):
        self.clear_grid()
        self.card_images = []
        CARD_WIDTH = 276
        CARD_HEIGHT = 390
        for index, path in enumerate(image_paths):
            try:
                img = Image.open(path)
                img = img.resize((CARD_WIDTH, CARD_HEIGHT))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(self.scrollable_frame, image=photo)
                label.image = photo
                row = index // self.columns
                col = index % self.columns
                label.grid(row=row, column=col, padx=5, pady=5)
                label.bind("<Button-1>", lambda e, path=path: self.show_card_details(path))

            except Exception as e:
                print(f"Fehler bei {path}: {e}")
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)
        
    def show_all_cards(self):
        self.only_user_cards = False
        self.display_images(self.all_img_paths)
        
    def show_user_cards(self):
        self.only_user_cards = True
        self.display_images(self.user_img_paths)
    
    def filter_cards(self, only_user_cards=False):
        typ = self.type_combobox.get()
        rarity = self.rarity_combobox.get()
        pack = self.pack_combobox.get()
        name = self.name_entry.get()

        # Mapping von Namen zu Index
        typ = self.type_map.get(typ) if typ else None
        rarity = self.rarity_map.get(rarity) if rarity else None
        pack = self.pack_map.get(pack) if pack else None

        # Sortierung lesen
        sort_crit = self.sort_combobox.get()
        
        if only_user_cards:
            img_names = get_filtered_img_names(user_id=self.user_id, name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=True, sort_by=sort_crit)
        else:
            img_names = get_filtered_img_names(name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=False, sort_by=sort_crit)

        base_path = os.getenv("PATH_ALL_CARDS")
        filtered_paths = [os.path.join(base_path, name) for name in img_names]
        self.display_images(filtered_paths)

    def reset_filters(self):
        self.type_combobox.set("")
        self.rarity_combobox.set("")
        self.pack_combobox.set("")
        self.name_entry.delete(0, tk.END)

        if self.only_user_cards:
            self.show_user_cards()
        else:
            self.show_all_cards()
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)
    
    def show_card_details(self, image_path: str):
        # Neues Toplevel-Fenster öffnen
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Kartendetails")

        detail_window.geometry("400x600")
        detail_window.resizable(False, False)

        try:
            img = Image.open(image_path)
            img = img.resize((360, 510))  # Größere Darstellung
            photo = ImageTk.PhotoImage(img)

            label = ttk.Label(detail_window, image=photo)
            label.image = photo 
            label.pack(padx=20, pady=20)

        except Exception as e:
            error_label = ttk.Label(detail_window, text=f"Fehler: {e}", bootstyle="danger")
            error_label.pack(padx=20, pady=20)
        
        detail_window.bind("<Escape>", lambda e: detail_window.destroy())

    def clear_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def update_scrollregion(self, event):
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=(0, 0, bbox[2], max(bbox[3], self.canvas.winfo_height())))

    def schedule_name_filter(self, event):
        if self.name_filter_after_id:
            self.root.after_cancel(self.name_filter_after_id)
        self.name_filter_after_id = self.root.after(300, lambda: self.filter_cards(self.only_user_cards))

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

        # Sortierung
        self.sort_label = ttk.Label(self.menu_frame, text="Sortieren nach:", bootstyle="secondary", font=("Helvetica bold", 15))
        self.sort_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(20,5))
        
        self.sort_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Name", "Typ", "Seltenheit", "Pack"])
        self.sort_combobox.grid(row=2, column=0, columnspan=2, pady=(5,10))
        self.sort_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Filter 
        self.filter_label = ttk.Label(self.menu_frame, text="Filter", bootstyle="secondary", font=("Helvetica bold", 15))
        self.filter_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10,8))

        # Name
        self.name_label = ttk.Label(self.menu_frame, text="Name:", bootstyle="secondary", font=("Helvetica", 14))
        self.name_label.grid(row=4, column=0, columnspan=2, sticky="w")

        self.name_entry = ttk.Entry(self.menu_frame, bootstyle="secondary")
        self.name_entry.grid(row=5, column=0, columnspan=2, padx=10, pady=(5,10), sticky="ew")
        self.name_entry.bind("<KeyRelease>", self.schedule_name_filter)

        # Typ Combobox
        self.type_label = ttk.Label(self.menu_frame, text="Typ:", bootstyle="secondary", font=("Helvetica", 14))
        self.type_label.grid(row=6, column=0, columnspan=2, sticky="w")

        self.type_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["","Pflanze", "Feuer", "Wasser", "Elektro", 
        "Psycho", "Kampf", "Finsternis", "Metall", "Fee", "Drache", "Farblos"])
        self.type_combobox.grid(row=7, column=0, columnspan=2, pady=(5,10))
        self.type_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.type_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.type_map = {"Pflanze": 1, "Feuer": 2, "Wasser": 3, "Elektro": 4, "Psycho": 5, "Kampf": 6, "Finsternis": 7, "Metall": 8, "Fee": 9, "Drache": 10, "Farblos": 11}

        # Seltenheit Combobox
        self.rarity_label = ttk.Label(self.menu_frame, text="Seltenheit:", bootstyle="secondary", font=("Helvetica", 14))
        self.rarity_label.grid(row=8, column=0, columnspan=2, sticky="w")

        self.rarity_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Common", "Uncommon", "Rare", "Double Rare", "Ultra Rare", "Art Rare", "Special Art Rare", "Secret Rare"])
        self.rarity_combobox.grid(row=9, column=0, columnspan=2, pady=(5,10))
        self.rarity_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.rarity_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.rarity_map = {"Common": 1, "Uncommon": 2, "Rare": 3, "Double Rare": 4, "Ultra Rare": 5, "Art Rare": 6, "Special Art Rare": 7, "Secret Rare": 8}

        # Päckchen Combobox
        self.pack_label = ttk.Label(self.menu_frame, text="Päckchen:",bootstyle="secondary", font=("Helvetica", 14))
        self.pack_label.grid(row=10, column=0, columnspan=2, sticky="w")

        self.pack_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Sonnen & Mond Zyklus", "Karmesin & Purpur Zyklus"])
        self.pack_combobox.grid(row=11, column=0, columnspan=2, pady=(5,10))
        self.pack_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.pack_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.pack_map = {"Sonnen & Mond Zyklus": 1, "Karmesin & Purpur Zyklus": 2}

        # Reset Button
        self.reset_button = ttk.Button(self.menu_frame, text="Reset", width=8, bootstyle="secondary", command=self.reset_filters)
        self.reset_button.grid(row=12, column=0, columnspan=2, padx=5, pady=10)

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
        self.scrollable_frame.bind("<Configure>", self.update_scrollregion)

        # Scrollable Frame oben links im Canvas platzieren
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Alle Spalten im scrollable_frame gleichmäßig verteilen
        self.scrollable_frame.columnconfigure(tuple(range(self.columns)), weight=1)

        # Mousewheel-Scrolling über das Canvas aktivieren
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) 


# Test
root = ttk.Window(themename="minty")
PokebookApp(root, "1", 1)
root.mainloop()
