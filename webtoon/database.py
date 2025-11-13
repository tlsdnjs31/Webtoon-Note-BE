import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "webtoon_database.sqlite")
DATABASE_URL = "sqlite:///./webtoon/webtoon_database.salite"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()