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
        cur.execute("SELECT Bildname FROM karte")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except mariadb.Error as e:
        print(f"DB Fehler: {e}")
        return []
    finally:
        cur.close()
        conn.close()

