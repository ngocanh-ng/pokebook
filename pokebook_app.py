import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import db
import csv
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import shutil

class PokebookApp:
    def __init__(self, root, username, user_id, is_admin=False):
        self.root = root
        self.username = username
        self.user_id = user_id
        self.is_admin = is_admin
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
        if not self.is_admin:
            self.all_cards_button.configure(bootstyle="primary")

        # Admin Theme
        if self.is_admin:
            self.reset_button.configure(bootstyle="secondary")
            self.scrollbar.configure(bootstyle="secondary-round")
            self.sort_label.configure(bootstyle="secondary")
            self.name_filter_label.configure(bootstyle="secondary")
            self.name_filter_entry.config(bootstyle="secondary")
            self.filter_label.configure(bootstyle="secondary")
            self.type_filter_label.configure(bootstyle="secondary")
            self.rarity_filter_label.configure(bootstyle="secondary")
            self.pack_filter_label.configure(bootstyle="secondary")
            self.counter_label.configure(bootstyle="secondary")
            self.add_card_menu()

    def get_all_img_paths(self):
        base_path = os.getenv("PATH_ALL_CARDS")
        all_img_names = db.get_all_img_names()
        return [os.path.join(base_path, name) for name in all_img_names]

    def get_user_img_paths(self):
        base_path = os.getenv("PATH_ALL_CARDS")
        user_img_names = db.get_user_img_names(self.user_id)
        return [os.path.join(base_path, name) for name in user_img_names]
    
    def change_button_colour(self, clicked_button, other_button):
        clicked_button.configure(bootstyle="primary")
        other_button.configure(bootstyle="primary.Outline.TButton")

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
        self.update_card_counter()
        
    def show_user_cards(self):
        self.only_user_cards = True
        self.display_images(self.user_img_paths)
        self.update_card_counter()
    
    def filter_cards(self, only_user_cards):
        typ = self.type_filter_combobox.get()
        rarity = self.rarity_filter_combobox.get()
        pack = self.pack_filter_combobox.get()
        name = self.name_filter_entry.get()

        # Mapping von Namen zu Index
        typ = self.type_map.get(typ) if typ else None
        rarity = self.rarity_map.get(rarity) if rarity else None
        pack = self.pack_map.get(pack) if pack else None

        # Sortierung lesen
        sort_crit = self.sort_combobox.get()
        
        if only_user_cards:
            img_names = db.get_filtered_img_names(user_id=self.user_id, name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=True, sort_by=sort_crit)
        else:
            img_names = db.get_filtered_img_names(name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=False, sort_by=sort_crit)

        base_path = os.getenv("PATH_ALL_CARDS")
        filtered_paths = [os.path.join(base_path, name) for name in img_names]
        self.display_images(filtered_paths)

    def reset_filters(self):
        self.type_combobox.set("")
        self.rarity_filter_combobox.set("")
        self.pack_filter_combobox.set("")
        self.name_filter_entry.delete(0, tk.END)

        if self.only_user_cards:
            self.show_user_cards()
        else:
            self.show_all_cards()
    
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

    def update_card_counter(self, total=None):
        total_cards = total if total is not None else len(self.all_img_paths)
        user_cards = len(self.user_img_paths)
        if self.is_admin: 
            self.counter_label.configure(text=f"{total_cards} Karten insgesamt")
        else:
            self.counter_label.configure(text=f"{total_cards} Karten insgesamt, {user_cards} in Sammlung")

    def export_collection_as_csv(self):
        if not self.is_admin:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")],initialfile="Meine_Sammlung.csv")
            data = db.get_user_img_details(self.user_id)
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")],initialfile="Komplette_Sammlung.csv")
            data = db.get_all_img_details()

        if not file_path:
            return
        
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Name", "Typ", "Seltenheit", "Päckchen"])
            for bildname, typ, seltenheit, pack in data:
                name_without_png = os.path.splitext(bildname)[0]
                writer.writerow([name_without_png, typ, seltenheit, pack])

    def export_collection_as_pdf(self):
        if not self.is_admin:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dateien", "*.pdf")], initialfile="Meine_Sammlung.pdf")
            data = db.get_user_img_details(self.user_id)
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dateien", "*.pdf")], initialfile="Komplette_Sammlung.pdf")
            data = db.get_all_img_details()

        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica", 12)
        if not self.is_admin:
            c.drawString(50, y, f"Pokémon-Kartensammlung von {self.username}")
        else:
            c.drawString(50, y, f" Komplette Pokémon-Kartensammlung")
        y -= 30
        c.setFont("Helvetica", 10)

        for bildname, typ, seltenheit, pack in data:
            name_without_png = os.path.splitext(bildname)[0]
            line = f"Name: {name_without_png} | Typ: {typ} | Seltenheit: {seltenheit} | Päckchen: {pack}"
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
    
    def setup_ui(self):
        # Menüleister
        menubar = ttk.Menu(self.root)
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportieren als PDF", command=self.export_collection_as_pdf)
        file_menu.add_command(label="Exportieren als CSV", command=self.export_collection_as_csv)
        file_menu.add_separator()
        menubar.add_cascade(label="Menü", menu=file_menu)
        file_menu.add_command(label="Logout")

        # Menüleiste setzen
        self.root.config(menu=menubar)

        # Menü-Frame
        self.menu_frame = ttk.Frame(self.root, borderwidth=10, relief = tk.GROOVE)
        self.menu_frame.grid(row=0, column=0, sticky="n", padx=(15,5))

        if not self.is_admin:
            # Alle Karten Button
            self.all_cards_button = ttk.Button(
                self.menu_frame, 
                text="Alle Karten", 
                bootstyle="primary.Outline.TButton", 
                width=10, 
                command=lambda:[self.show_all_cards(), self.change_button_colour(self.all_cards_button, self.my_cards_button)])
            self.all_cards_button.grid(row=0, column=0)

            # Meine Karten Button
            self.my_cards_button = ttk.Button(
                self.menu_frame, 
                text="Meine Karten",
                bootstyle="primary.Outline.TButton",
                width=10,
                command=lambda:[self.show_user_cards(), self.change_button_colour(self.my_cards_button, self.all_cards_button)])
            self.my_cards_button.grid(row=0, column=1)
        else:
            self.admin_label = ttk.Label(self.menu_frame, text="Admin-Bereich", bootstyle="secondary", font=("Arial bold", 18) )
            self.admin_label.grid(row=0, column=0, columnspan=2, pady=5)
            self.menu_separator = ttk.Separator(self.menu_frame, bootstyle="secondary")
            self.menu_separator.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Sortierung
        self.sort_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Sortieren nach:", font=("Arial bold", 15))
        self.sort_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(15,5))
        
        self.sort_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Name", "Typ", "Seltenheit", "Pack"])
        self.sort_combobox.grid(row=3, column=0, columnspan=2, pady=(5,10))
        self.sort_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Filter 
        self.filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Filter", font=("Arial bold", 15))
        self.filter_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(5,8))

        # Name
        self.name_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Name:", font=("Arial", 14))
        self.name_filter_label.grid(row=5, column=0, columnspan=2, sticky="w")

        self.name_filter_entry = ttk.Entry(self.menu_frame, bootstyle="primary")
        self.name_filter_entry.grid(row=6, column=0, columnspan=2, pady=(5,10))
        self.name_filter_entry.bind("<KeyRelease>", self.schedule_name_filter)

        # Typ Combobox
        self.type_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Typ:", font=("Arial", 14))
        self.type_filter_label.grid(row=7, column=0, columnspan=2, sticky="w")

        self.type_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["","Pflanze", "Feuer", "Wasser", "Elektro", 
        "Psycho", "Kampf", "Finsternis", "Metall", "Fee", "Drache", "Farblos"])
        self.type_combobox.grid(row=8, column=0, columnspan=2, pady=(5,10))
        self.type_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.type_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.type_map = {"Pflanze": 1, "Feuer": 2, "Wasser": 3, "Elektro": 4, "Psycho": 5, "Kampf": 6, "Finsternis": 7, "Metall": 8, "Fee": 9, "Drache": 10, "Farblos": 11}

        # Seltenheit Combobox
        self.rarity_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Seltenheit:", font=("Arial", 14))
        self.rarity_filter_label.grid(row=9, column=0, columnspan=2, sticky="w")

        self.rarity_filter_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Common", "Uncommon", "Rare", "Double Rare", "Ultra Rare", "Art Rare", "Special Art Rare", "Secret Rare"])
        self.rarity_filter_combobox.grid(row=10, column=0, columnspan=2, pady=(5,10))
        self.rarity_filter_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.rarity_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.rarity_map = {"Common": 1, "Uncommon": 2, "Rare": 3, "Double Rare": 4, "Ultra Rare": 5, "Art Rare": 6, "Special Art Rare": 7, "Secret Rare": 8}

        # Päckchen Combobox
        self.pack_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Päckchen:", font=("Arial", 14))
        self.pack_filter_label.grid(row=11, column=0, columnspan=2, sticky="w")

        self.pack_filter_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=["", "Reisegefährten", "Welten im Wandel"])
        self.pack_filter_combobox.grid(row=12, column=0, columnspan=2, pady=(5,10))
        self.pack_filter_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.pack_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))
        self.pack_map = {"Reisegefährten": 1, "Welten im Wandel": 2}

        # Reset Button
        self.reset_button = ttk.Button(self.menu_frame, bootstyle="primary", text="Reset", width=8, command=self.reset_filters)
        self.reset_button.grid(row=13, column=0, columnspan=2, padx=5, pady=10)

        # Karten-Zähler
        self.counter_label = ttk.Label(self.menu_frame, text="", bootstyle="primary", font=("Arial", 13))
        if not self.is_admin:
            self.counter_label.grid(row=14, column=0, columnspan=2, pady=(10, 0))
        else:
            self.counter_label.grid(row=25, column=0, columnspan=2, pady=(10, 0))

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
        self.scrollbar = ttk.Scrollbar(self.container, bootstyle="primary-round", orient="vertical", command=self.canvas.yview)
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

    def select_image(self):
        path = filedialog.askopenfilename(title="Bild auswählen", filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.gif")])
        if path:
            self.image_filename = path
            messagebox.showinfo("Bild ausgewählt", os.path.basename(path))
    
    def add_cards(self):
        name = self.name_add_entry.get().strip()
        typ_name = self.typ_combobox.get()
        seltenheit_name = self.seltenheit_combobox.get()
        pack_name = self.pack_add_combobox.get()

        if not all([name, typ_name, seltenheit_name, pack_name, self.image_filename]):
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen und ein Bild auswählen.")
            return

        typ_id = db.get_id("typ", typ_name)
        seltenheit_id = db.get_id("seltenheit", seltenheit_name)
        pack_id = db.get_id("paeckchen", pack_name)

        if not all([typ_id, seltenheit_id, pack_id]):
            messagebox.showerror("Fehler", "Ungültige Auswahl in den Drop-down-Feldern.")
            return

        try:
            image_name = os.path.basename(self.image_filename)
            target_path = os.path.join("assets/Karten_Bilder", image_name)
            shutil.copy(self.image_filename, target_path)
        except Exception as e:
            messagebox.showerror("Bildfehler", f"Bild konnte nicht kopiert werden: {e}")
            return
        
        db.add_cards_to_db(messagebox, name, typ_id, seltenheit_id, pack_id, image_name)
        self.clearform()
    
    def clear_form(self):
        self.name_add_entry.delete(0, 'end')
        self.typ_combobox.set('')
        self.seltenheit_combobox.set('')
        self.pack_add_combobox.set('')
        self.image_filename = None
    
    def add_card_menu(self):
        self.add_cards_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Karten hinzufügen", font=("Arial bold", 14))
        self.add_cards_label.grid(row=14, column=0, pady=(5,0), sticky="w")

        self.name_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Name:", font=("Arial", 14))
        self.name_add_label.grid(row=15, column=0, sticky="w", pady=5)
        self.name_add_entry = ttk.Entry(self.menu_frame, bootstyle="secondary")
        self.name_add_entry.grid(row=16, column=0, columnspan=2)

        self.typ_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Typ", font=("Arial", 14))
        self.typ_add_label.grid(row=17, column=0, sticky="w", pady=5)
        self.typ_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=db.get_options("typ"))
        self.typ_combobox.grid(row=18, column=0, columnspan=2, padx=5)

        self.seltenheit_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Seltenheit", font=("Arial", 14))
        self.seltenheit_add_label.grid(row=19, column=0, sticky="w", pady=5)
        self.seltenheit_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=db.get_options("seltenheit"))
        self.seltenheit_combobox.grid(row=20, column=0, columnspan=2, padx=5)

        self.pack_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Päckchen", font=("Arial", 14))
        self.pack_add_label.grid(row=21, column=0, sticky="w", pady=5)
        self.pack_add_combobox = ttk.Combobox(self.menu_frame, state="readonly", values=db.get_options("paeckchen"))
        self.pack_add_combobox.grid(row=22, column=0, columnspan=2, padx=5)

        self.upload_button = ttk.Button(self.menu_frame, bootstyle="secondary.Outline.TButton", text="Bild auswählen", command=self.select_image)
        self.upload_button.grid(row=23, column=0, columnspan=2, pady=10)

        self.add_button = ttk.Button(self.menu_frame, bootstyle="secondary", text="Karte hinzufügen", command=self.add_cards)
        self.add_button.grid(row=24, column=0, columnspan=2, pady=10)        

# Test
root = ttk.Window(themename="minty")
PokebookApp(root, "Ngoc Anh", 4, is_admin=True)
root.mainloop()
