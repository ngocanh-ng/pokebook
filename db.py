import mariadb
import sys 
from dotenv import load_dotenv
import os

load_dotenv()

def get_all_img_names():
    try:
        connection = mariadb.connect(
            user = os.getenv("USER"),
            password = os.getenv("PASSWORD"),
            host = os.getenv("HOST"),
            port = 3306,
            database = "team02")
 
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB PLatform: {e}")
        sys.exit(1)
        
    cursor = connection.cursor()
    cursor.execute("SELECT Bildname FROM karte")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


