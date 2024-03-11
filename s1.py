import db
import hashlib
import os
import time
import sqlite3

TIME_FORMAT = "%d-%b-%Y %I:%M:%S %p"

def calculate_checksum(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def tamper_check(filepath):
    if db.is_exist(filepath):
        checksum_from_db = db.fetch_hash(filepath)
        current_checksum = calculate_checksum(filepath)
        if checksum_from_db != current_checksum:
            print("File has been tampered with!")
            db.tampered(filepath)
        else:
            print("File has not been tampered with.")
            db.not_tampered(filepath)


def log(filepath):
    filename = os.path.basename(filepath)
    last_opened = time.strftime(TIME_FORMAT)
    last_modified = time.strftime(TIME_FORMAT, time.localtime(int(os.path.getmtime(filepath))))
    checksum = calculate_checksum(filepath)
    #db.insert_in_db(filepath, filename, last_opened, last_modified, checksum, "UNALTERED")
    tamper_check(filepath)

def check_for_altered_files():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Query for altered files
    cursor.execute("SELECT filename FROM files WHERE status=?", ("ALTERED",))
    altered_files = cursor.fetchall()

    if altered_files:
        print("Altered files detected:")
        for file in altered_files:
            print(file[0])  # Print the filename
    else:
        print("No altered files detected.")

    conn.close()
