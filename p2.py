import sqlite3
import hashlib
import os
import time

# Connect to SQLite database
conn = sqlite3.connect('file_info.db')
c = conn.cursor()

# Create table to store file information
c.execute('''CREATE TABLE IF NOT EXISTS files
             (filename TEXT, last_opened INTEGER, last_modified INTEGER, checksum TEXT)''')

# Function to calculate checksum
def calculate_checksum(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to store file information in the database
def store_file_info(file_path):
    filename = os.path.basename(file_path)
    last_opened = int(time.time())
    last_modified = int(os.path.getmtime(file_path))
    checksum = calculate_checksum(file_path)
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?)", (filename, last_opened, last_modified, checksum))
    conn.commit()
    print("File information stored successfully.")

# Function to check for tampering
def check_for_tampering(file_path):
    stored_checksum = c.execute("SELECT checksum FROM files WHERE filename=?", (os.path.basename(file_path),)).fetchone()[0]
    current_checksum = calculate_checksum(file_path)
    if stored_checksum != current_checksum:
        print("File has been tampered with!")
    else:
        print("File has not been tampered with.")

# Example usage
file_path = 'example.txt'
store_file_info(file_path)
time.sleep(1)  # Simulating some time passing
check_for_tampering(file_path)

# Close database connection
conn.close()
