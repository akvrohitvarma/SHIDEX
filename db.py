import sqlite3
import os

path = os.getcwd()
db_path = f"{path}/sh1d3x_auditor.db"

def create_db():
    conn = sqlite3.connect(f"{path}/sh1d3x_auditor.db")
    conn.close()

def initialize_db():
    if not os.path.exists(db_path):
        create_db()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS files(filepath TEXT UNIQUE, filename TEXT, last_opened TEXT, last_modified TEXT, checksum TEXT, status TEXT)")
        conn.close()
    else:
        pass

def insert_in_db(filepath, filename, last_opened, last_modified, checksum, status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?)", (filepath, filename, last_opened, last_modified, checksum, status))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("File with the same filename already exists in the database.")

def fetch_hash(filepath):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    checksum = cursor.execute("SELECT checksum FROM files WHERE filepath=?", (filepath,)).fetchone()[0]
    conn.commit()
    conn.close()
    return checksum

def is_exist(filepath):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        filepath_from_db = cursor.execute("SELECT filepath FROM files WHERE filepath=?", (filepath,)).fetchone()[0]
        return filepath_from_db == filepath
    except TypeError:
        return False
    
def tampered(filepath):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE files SET status=? WHERE filepath=?", ("ALTERED", filepath))
    conn.commit()
    conn.close()

def not_tampered(filepath):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE files SET status=? WHERE filepath=?", ("UNALTERED", filepath))
    conn.commit()
    conn.close()

#print(is_exist("/Users/rohit/Documents/my-python-projects/shidex/fileLogging/div.txt"))

not_tampered("/Users/rohit/Documents/my-python-projects/shidex/fileLogging/example.txt")
#initialize_db()
#fetch_hash("/Users/rohit/Documents/my-python-projects/shidex/fileLogging/example.txt")