from tkinter import filedialog
import db
import csv
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_collection_as_csv(self):
        if not self.is_admin:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")],initialfile="Meine_Sammlung.csv")
            data = db.get_user_card_details(self.user_id)
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")],initialfile="Komplette_Sammlung.csv")
            data = db.get_all_card_details()

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
        data = db.get_user_card_details(self.user_id)
    else:
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dateien", "*.pdf")], initialfile="Komplette_Sammlung.pdf")
        data = db.get_all_card_details()

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