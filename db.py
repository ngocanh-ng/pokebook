import mariadb
import sys 
from dotenv import load_dotenv
import os

load_dotenv()

def connect_db():
    try:
        connection = mariadb.connect(
            user=os.getenv("LOCAL_USER"),
            password=os.getenv("LOCAL_PASSWORD"),
            host=os.getenv("LOCAL_HOST"),
            port=3307,
            database="team02"
        )
        return connection
    except mariadb.Error as e:
        print(f"Fehler beim Verbinden zur MariaDB: {e}")
        sys.exit(1)

def get_all_img_names():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT Bildname FROM karte ORDER BY Bildname")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except mariadb.Error as e:
        print(f"DB Fehler: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_user_img_names(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT karte.Bildname FROM zuordnung_benutzer_karte INNER JOIN benutzer ON zuordnung_benutzer_karte.Benutzer = benutzer.BenutzerID INNER JOIN karte ON zuordnung_benutzer_karte.Karte = karte.KarteID WHERE benutzer = %s ORDER BY Bildname", (user_id,))
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except mariadb.Error as e:
        print(f"DB Fehler: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_filtered_img_names(user_id = None, name=None, typ = None, rarity = None, pack = None, only_user_cards = False, sort_by = None):
    try: 
        conn = connect_db()
        cur = conn.cursor()
        
        if only_user_cards and user_id:
            query = "SELECT karte.Bildname FROM zuordnung_benutzer_karte INNER JOIN benutzer ON zuordnung_benutzer_karte.Benutzer = benutzer.BenutzerID INNER JOIN karte ON zuordnung_benutzer_karte.Karte = karte.KarteID WHERE benutzer = %s"
            params = [user_id]
        else:
            query = "SELECT Bildname FROM karte WHERE 1=1"
            params = [] 

        if typ:
            query += " AND Typ = %s"
            params.append(typ)
        if rarity:
            query += " AND Seltenheit = %s"
            params.append(rarity)
        if pack:
            query += " AND Paeckchen = %s"
            params.append(pack)
        if name:
            query += " AND karte.Name LIKE %s"
            params.append(f"%{name}%")

        sort_field_map = {
        "Name": "karte.Name",
        "Typ": "karte.Typ",
        "Seltenheit": "karte.Seltenheit",
        "Päckchen": "karte.Paeckchen"
        }

        if sort_by in sort_field_map:
            query += f" ORDER BY {sort_field_map[sort_by]} ASC"

        cur.execute(query, tuple(params))
        return [row[0] for row in cur.fetchall()]

    except mariadb.Error as e:
        print(f"DB Fehler: {e}")
        return []
    finally:
        cur.close()
        conn.close()

import sqlite3
import os

def get_user_img_details(user_id):
    try:
        conn = connect_db()
        cur = conn.cursor()

        query = "SELECT karte.Bildname, typ.Name, seltenheit.Name, paeckchen.Name FROM zuordnung_benutzer_karte INNER JOIN karte ON zuordnung_benutzer_karte.Karte = karte.KarteID INNER JOIN typ ON karte.Typ = typ.TypID INNER JOIN seltenheit ON karte.Seltenheit = seltenheit.SeltenheitID INNER JOIN paeckchen ON karte.Paeckchen = paeckchen.PaeckchenID WHERE zuordnung_benutzer_karte.Benutzer = %s ORDER BY karte.Bildname ASC"
        cur.execute(query, (user_id,))

        result = cur.fetchall()
        return result
    
    except mariadb.Error as e:
        print(f"DB Fehler: {e}")
        return []
    finally:
        cur.close()
        conn.close()
