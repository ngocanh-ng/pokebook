import tkinter as tk
import ttkbootstrap as ttk
import os
from PIL import Image, ImageTk
import db
import csv
from tkinter import filedialog, messagebox
import export
from constants import TYPE_MAP, RARITY_MAP, PACK_MAP
import shutil
import sys


class PokebookApp:
    def __init__(self, root, username, user_id, is_admin=False):
        self.root = root
        self.username = username
        self.user_id = user_id
        self.is_admin = is_admin
        self.columns = 4
        self.root.title(f"Pokébook – {username}")

        self.card_id = None
        self.card_name = None

        # Button-Größe
        s = ttk.Style()
        s.configure("TButton", font=("Helvetica", 11))

        # Grid-Konfiguration zurücksetzen
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Pfade für Bilder 
        self.all_img_paths = self.get_all_img_paths()
        self.user_img_paths = self.get_user_img_paths()
        
        # Flags
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

    def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def get_all_img_paths(self):
        base_path =  self.resource_path("assets/Karten_Bilder")
        all_img_names = db.get_all_img_names()
        return [os.path.join(base_path, name) for name in all_img_names]

    def get_user_img_paths(self):
        base_path = self.resource_path("assets/Karten_Bilder")
        user_img_names = db.get_user_img_names(self.user_id)
        return [os.path.join(base_path, name) for name in user_img_names]
    
    def change_collection_button_colour(self, clicked_button, other_button):
        clicked_button.configure(bootstyle="primary")
        other_button.configure(bootstyle="primary.Outline.TButton")

    def display_images(self, image_paths, mode):
        self.clear_grid()
        self.card_images = []

        container_width = self.canvas.winfo_width()
        if container_width <= 1:  
            self.root.update_idletasks()
            container_width = self.canvas.winfo_width()

        padding = 10
        total_padding = (self.columns + 1) * padding
        card_area_width = container_width - total_padding
        card_width = max(100, card_area_width // self.columns)
        card_height = round(card_width * 1.41)

        for index, path in enumerate(image_paths):
            try:
                img = Image.open(path)
                img = img.resize((card_width, card_height))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(self.scrollable_frame, image=photo)
                label.image = photo
                row = index // self.columns
                col = index % self.columns
                label.grid(row=row, column=col, padx=5, pady=5)
                label.bind("<Button-1>", lambda e, path=path: self.show_card_details(path, mode))
            except Exception as e:
                print(f"Fehler bei {path}: {e}")
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)
        
    def show_all_cards(self):
        self.only_user_cards = False
        self.display_images(self.all_img_paths, "add")
        self.update_card_counter()
        
    def show_user_cards(self):
        self.only_user_cards = True
        self.display_images(self.user_img_paths, "delete")
        self.update_card_counter()
    
    def filter_cards(self, only_user_cards):
        typ = self.type_filter_combobox.get()
        rarity = self.rarity_filter_combobox.get()
        pack = self.pack_filter_combobox.get()
        name = self.name_filter_entry.get()

        # Mapping von Namen zu Index
        typ = TYPE_MAP.get(typ) if typ else None
        rarity = RARITY_MAP.get(rarity) if rarity else None
        pack = PACK_MAP.get(pack) if pack else None

        # Sortierung lesen
        sort_crit = self.sort_combobox.get()
        
        if only_user_cards:
            img_names = db.get_filtered_img_names(user_id=self.user_id, name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=True, sort_by=sort_crit)
        else:
            img_names = db.get_filtered_img_names(name=name, typ=typ, rarity=rarity, pack=pack, only_user_cards=False, sort_by=sort_crit)

        base_path = self.resource_path("assets/Karten_Bilder")
        filtered_paths = [os.path.join(base_path, name) for name in img_names]
        self.display_images(filtered_paths, "add")

    def reset_filters(self):
        self.type_filter_combobox.set("")
        self.rarity_filter_combobox.set("")
        self.pack_filter_combobox.set("")
        self.name_filter_entry.delete(0, tk.END)
        self.sort_combobox.set("")

        if self.only_user_cards:
            self.show_user_cards()
        else:
            self.show_all_cards()
    
    def show_card_details(self, image_path: str, mode="add"):
        self.detail_window = tk.Toplevel(self.root)
        self.detail_window.title("Kartendetails")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.detail_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.detail_window.resizable(False, False)

   

        try:
            img = Image.open(image_path)
            img = img.resize((360, 510))
            photo = ImageTk.PhotoImage(img)

            label = ttk.Label(self.detail_window, image=photo)
            label.image = photo
            label.pack(pady=5, padx=5)

            self.card_name = os.path.splitext(os.path.basename(image_path))[0]
            self.card_id = db.get_id("Karte", self.card_name)

            if mode == "add":
                add_button = ttk.Button(self.detail_window, text="Hinzufügen", command=lambda:[self.add_card(),self.detail_window.destroy()])
                add_button.pack(pady=(20, 10), padx=20, fill='x')
            elif mode == "delete":
                delete_button = ttk.Button(self.detail_window, text="Löschen", command=lambda:[self.delete_card(),self.detail_window.destroy()])
                delete_button.pack(pady=(20, 10), padx=20, fill='x')

        except Exception as e:
            error_label = ttk.Label(self.detail_window, text=f"Fehler: {e}", bootstyle="danger")
            error_label.pack(padx=20, pady=20)


    def add_card(self): #, card_id, card_name
        try:
            cur = db.connect_db().cursor()  # Stelle sicher, dass du die Verbindung hierher bekommst

            # Prüfen, ob die Karte bereits vorhanden ist
            cur.execute(
                "SELECT 1 FROM zuordnung_benutzer_karte WHERE Benutzer = ? AND Karte = ?",
                (self.user_id, self.card_id)
            )
            result = cur.fetchone()
            if result:
                messagebox.showinfo("Hinweis", f"Karte '{self.card_name}' ist bereits in deiner Sammlung.")
            else:
                db.new_User_card(self.user_id, self.card_id, messagebox, self.card_name)
                self.user_img_paths = self.get_user_img_paths()  # Aktualisiere die Pfade
                if self.only_user_cards:
                    self.show_user_cards() 
                else:
                    self.show_all_cards()# Aktualisierte Sammlung anzeigen

        except Exception as e:
            messagebox.showerror("Fehler", f"Datenbankfehler:\n{str(e)}")

    def delete_card(self):
        try:
            conn = db.connect_db()
            cur = conn.cursor()
            print(1)
            cur.execute(
                "DELETE FROM zuordnung_benutzer_karte WHERE Benutzer = ? AND Karte = ?",
                (self.user_id, self.card_id)
            )
            print(2)
            conn.commit()
            messagebox.showinfo("Erfolg", f"Karte '{self.card_name}' wurde gelöscht!")
            
            # Sammlung aktualisieren
            self.user_img_paths = self.get_user_img_paths()
            if self.only_user_cards:
                self.show_user_cards()

            cur.close()
            conn.close()

        except Exception as e:
            print(e)
            messagebox.showerror("Fehler", f"Datenbankfehler beim Löschen:\n{str(e)}")


    def clear_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")

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

    def logout(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from login import LoginApp
        LoginApp(self.root)

    # Hauptfenster
    def setup_ui(self):
        # Menüleister
        menubar = ttk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportieren als PDF", command=lambda: export.export_collection_as_pdf(self))
        file_menu.add_command(label="Exportieren als CSV", command=lambda: export.export_collection_as_csv(self))
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)

        menubar.add_cascade(label="Menü", menu=file_menu)

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
                width=11, 
                command=lambda:[self.show_all_cards(), self.change_collection_button_colour(self.all_cards_button, self.my_cards_button)])
            self.all_cards_button.grid(row=0, column=0, sticky="e")

            # Meine Karten Button
            self.my_cards_button = ttk.Button(
                self.menu_frame, 
                text="Meine Karten",
                bootstyle="primary.Outline.TButton",
                width=11,
                command=lambda:[self.show_user_cards(), self.change_collection_button_colour(self.my_cards_button, self.all_cards_button)])
            self.my_cards_button.grid(row=0, column=1, sticky="w")
        else:
            self.admin_label = ttk.Label(self.menu_frame, text="Admin-Bereich", bootstyle="secondary", font=("Arial", 13, "bold") )
            self.admin_label.grid(row=0, column=0, columnspan=2, pady=(0,5))
            self.menu_separator = ttk.Separator(self.menu_frame, bootstyle="secondary")
            self.menu_separator.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Sortierung
        self.sort_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Sortieren:", font=("Arial", "12","bold"))
        self.sort_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(15,5))
        
        self.sort_combobox = ttk.Combobox(self.menu_frame, width=28, state="readonly", values=["", "Name", "Typ", "Seltenheit", "Päckchen"])
        self.sort_combobox.grid(row=3, column=0, columnspan=2, pady=(5,10))
        self.sort_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Filter 
        self.filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Filter:", font=("Arial", "12","bold"))
        self.filter_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(5,8))

        # Name
        self.name_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Name:", font=("Arial", "11", "bold"))
        self.name_filter_label.grid(row=5, column=0, columnspan=2, sticky="w")

        self.name_filter_entry = ttk.Entry(self.menu_frame, bootstyle="primary", width=30)
        self.name_filter_entry.grid(row=6, column=0, columnspan=2, pady=(5,10))
        self.name_filter_entry.bind("<KeyRelease>", self.schedule_name_filter)

        # Typ Combobox
        self.type_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Typ:", font=("Arial", "11", "bold"))
        self.type_filter_label.grid(row=7, column=0, columnspan=2, sticky="w")

        self.type_filter_combobox = ttk.Combobox(
            self.menu_frame, 
            width=28, 
            state="readonly", 
            values=["","Pflanze", "Feuer", "Wasser", "Elektro", "Psycho", "Kampf", "Finsternis", "Metall", "Fee", "Drache", "Farblos"]
            )
        self.type_filter_combobox.grid(row=8, column=0, columnspan=2, pady=(5,10))
        self.type_filter_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.type_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Seltenheit Combobox
        self.rarity_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Seltenheit:", font=("Arial", "11", "bold"))
        self.rarity_filter_label.grid(row=9, column=0, columnspan=2, sticky="w")

        self.rarity_filter_combobox = ttk.Combobox(
            self.menu_frame,
            width=28, 
            state="readonly", 
            values=["", "Common", "Uncommon", "Rare", "Double Rare", "Ultra Rare", "Art Rare", "Special Art Rare", "Secret Rare"]
            )
        self.rarity_filter_combobox.grid(row=10, column=0, columnspan=2, pady=(5,10))
        self.rarity_filter_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.rarity_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Päckchen Combobox
        self.pack_filter_label = ttk.Label(self.menu_frame, bootstyle="primary", text="Päckchen:", font=("Arial", "11", "bold"))
        self.pack_filter_label.grid(row=11, column=0, columnspan=2, sticky="w")

        self.pack_filter_combobox = ttk.Combobox(
            self.menu_frame,
            width = 28, 
            state="readonly", 
            values=["", "Reisegefährten", "Welten im Wandel"]
            )
        self.pack_filter_combobox.grid(row=12, column=0, columnspan=2, pady=(5,10))
        self.pack_filter_combobox.bind("<Return>", lambda event: self.filter_cards(only_user_cards=self.only_user_cards))
        self.pack_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_cards(self.only_user_cards))

        # Reset Button
        self.reset_button = ttk.Button(self.menu_frame, bootstyle="primary", text="Reset", width=8, command=self.reset_filters)
        self.reset_button.grid(row=13, column=0, columnspan=2, padx=5, pady=10)

        # Karten-Zähler
        self.counter_label = ttk.Label(self.menu_frame, text="", bootstyle="primary", font=("Arial", "10"))
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
        self.canvas.bind("<Configure>", lambda e: self.display_images(self.user_img_paths if self.only_user_cards else self.all_img_paths,
    "delete" if self.only_user_cards else "add"))


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
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

    # Admin Features
    def select_image(self):
        path = filedialog.askopenfilename(title="Bild auswählen", filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.webp")])
        if path:
            self.image_filename = path
            messagebox.showinfo("Bild ausgewählt", f'"{os.path.basename(path)}" ausgewählt!')
    
    def add_card_admin(self):
        name = self.name_add_entry.get().strip()
        type_name = self.type_add_combobox.get()
        rarity_name = self.rarity_add_combobox.get()
        pack_name = self.pack_add_combobox.get()

        if not all([name, type_name, rarity_name, pack_name, self.image_filename]):
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen und ein Bild auswählen.")
            return

        type_id = db.get_id("typ", type_name)
        rarity_id = db.get_id("seltenheit", rarity_name)
        pack_id = db.get_id("paeckchen", pack_name)

        if not all([type_id, rarity_id, pack_id]):
            messagebox.showerror("Fehler", "Ungültige Auswahl in den Drop-down-Feldern.")
            return

        try:
            image_name = os.path.basename(self.image_filename)
            target_path = os.path.join("assets/Karten_Bilder", image_name)
            shutil.copy(self.image_filename, target_path)
        except Exception as e:
            messagebox.showerror("Bildfehler", f"Bild konnte nicht kopiert werden: {e}")
            return
        
        db.add_new_card_admin(messagebox, name, type_id, rarity_id, pack_id, image_name)
        self.clear_add_card_form()
        self.refresh_grid()
    
    def refresh_grid(self):
        self.all_img_paths = self.get_all_img_paths()
        self.display_images(self.all_img_paths)
        self.update_card_counter()
    
    def clear_add_card_form(self):
        self.name_add_entry.delete(0, 'end')
        self.typ_combobox.set('')
        self.seltenheit_combobox.set('')
        self.pack_add_combobox.set('')
        self.image_filename = None
    
    def add_card_menu(self):
        self.add_card_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Karten hinzufügen", font=("Arial", 13, "bold"))
        self.add_card_label.grid(row=14, column=0, columnspan=2, pady=(5,0))

        self.name_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Name:", font=("Arial", 11, "bold"))
        self.name_add_label.grid(row=15, column=0, sticky="w", pady=5)
        self.name_add_entry = ttk.Entry(self.menu_frame, bootstyle="secondary", width=30)
        self.name_add_entry.grid(row=16, column=0, columnspan=2)

        self.type_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Typ:", font=("Arial", 11, "bold"))
        self.type_add_label.grid(row=17, column=0, sticky="w", pady=5)
        self.type_add_combobox = ttk.Combobox(self.menu_frame, width=28, state="readonly", values=db.get_options("typ"))
        self.type_add_combobox.grid(row=18, column=0, columnspan=2, padx=5)

        self.rarity_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Seltenheit", font=("Arial", 11, "bold"))
        self.rarity_add_label.grid(row=19, column=0, sticky="w", pady=5)
        self.rarity_add_combobox = ttk.Combobox(self.menu_frame, width=28, state="readonly", values=db.get_options("seltenheit"))
        self.rarity_add_combobox.grid(row=20, column=0, columnspan=2, padx=5)

        self.pack_add_label = ttk.Label(self.menu_frame, bootstyle="secondary", text="Päckchen", font=("Arial", 11, "bold"))
        self.pack_add_label.grid(row=21, column=0, sticky="w", pady=5)
        self.pack_add_combobox = ttk.Combobox(self.menu_frame, width=28, state="readonly", values=db.get_options("paeckchen"))
        self.pack_add_combobox.grid(row=22, column=0, columnspan=2, padx=5)

        self.upload_button = ttk.Button(self.menu_frame, bootstyle="secondary.Outline.TButton", text="Bild auswählen", command=self.select_image)
        self.upload_button.grid(row=23, column=0, columnspan=2, pady=(20,15))

        self.add_button = ttk.Button(self.menu_frame, bootstyle="secondary", text="Karte hinzufügen", command=self.add_card_admin)
        self.add_button.grid(row=24, column=0, columnspan=2, pady=10)        