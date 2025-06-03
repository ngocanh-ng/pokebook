import mariadb
import bcrypt
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from db import connect_db 
from pokebook_app import PokebookApp 
import ttkbootstrap as ttk 
from dotenv import load_dotenv 
import os 
load_dotenv() 


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokébook") 

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 350
        window_height = 350
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        try:
            img = Image.open("assets/pokeball.png") 
            img = img.resize((32, 32), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, self.icon)
        except Exception as e:
            print(f"Fehler beim Laden des Icons: {e}")
       
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

        self.root.grid_columnconfigure(0, weight=1)  
        self.root.grid_columnconfigure(1, weight=0) 
        self.root.grid_columnconfigure(2, weight=1) 

        username_label = ttk.Label(self.root, text="Benutzername:", font=("Helvetica", 13))
        username_label.grid(row=0, column=1, pady=15, padx=10, sticky="e")

        self.username_entry = ttk.Entry(self.root, width=20)
        self.username_entry.grid(row=0, column=2, pady=15, padx=10, sticky="w")

        password_label = ttk.Label(self.root, text="Passwort:", font=("Helvetica", 13))
        password_label.grid(row=1, column=1, pady=15, padx=10, sticky="e")

        self.password_entry = ttk.Entry(self.root, show="*", width=20)
        self.password_entry.grid(row=1, column=2, pady=15, padx=10, sticky="w")

        self.login_button = ttk.Button(root, text="Anmelden", bootstyle="secondary", command=self.login
        )
        self.login_button.grid(row=2, column=0, columnspan=3, pady=15) # Anh: Login-Button neu positioniert

        self.username_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.bind("<Return>", lambda event: self.login())

        try:
            logo_img = Image.open("assets/logo.png") 
            base_width = 300
            w_percent = (base_width / float(logo_img.size[0]))
            h_size = int((float(logo_img.size[1]) * float(w_percent)))
            logo_img = logo_img.resize((base_width, h_size), Image.LANCZOS)

            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(self.root, image=self.logo_photo)
            logo_label.grid(row=3, column=0, columnspan=3, pady=(5, 10))
        except Exception as e:
            print(f"Error loading logo image: {e}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben!")
            return

        try: 
            query = "SELECT BenutzerID, PasswortHash, is_admin FROM benutzer WHERE benutzername = %s" 
            self.cursor.execute(query, (username,))
            result = self.cursor.fetchone()
        except mariadb.Error as e:
            messagebox.showerror("Datenbankfehler", f"Abfrage fehlgeschlagen: {e}")
            return

        if result:
            user_id, stored_hash, is_admin = result[0], result[1].encode('utf-8'), result[2]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                for widget in self.root.winfo_children():
                    widget.destroy()
                PokebookApp(self.root, username, user_id, is_admin=bool(is_admin))
                # neue Fenstergröße und Position
                self.root.update_idletasks()
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                window_width = 1910
                window_height = 1050
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                self.root.geometry(f"{window_width}x{window_height}+{x-10}+{y-60}")
            else:
                messagebox.showerror("Fehler", "Falsches Passwort!")

        else:
            messagebox.showerror("Fehler", "Benutzer nicht gefunden!")

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'db'):
            self.db.close()


