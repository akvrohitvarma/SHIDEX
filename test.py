import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import imghide
        
MAX_FILE_SIZE = 2 * 1024 * 1024  # Maximum file size in bytes (2 MB)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SHIDEX")
        self.geometry("800x600")

        # Main Frame
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill="both")

        label = tk.Label(main_frame, text="SHIDEX by Team 3", font=('Arial', 32))
        label.pack(side="top", fill="x", pady=20)

        # Top Frame
        top_frame = tk.Frame(main_frame, bd=3, relief="flat")
        top_frame.pack(side="top", fill="x", padx=40)

        # Column 1 Frame
        col1_frame = tk.Frame(top_frame)
        col1_frame.pack(side="left")

        # Image Canvas in Column 1 Frame
        self.image_canvas_col1 = tk.Canvas(col1_frame, width=300, height=200, bg="white")
        self.image_canvas_col1.grid(row=0, column=0, pady=10)
        self.placeholder_image = Image.open(".\\assets\\encode.png")  # Update with your placeholder image file path
        self.placeholder_image = self.placeholder_image.resize((300, 200), Image.LANCZOS)
        self.placeholder_photo = ImageTk.PhotoImage(self.placeholder_image)
        self.image_canvas_col1.create_image(150, 100, image=self.placeholder_photo)

        # Buttons in Column 1 Frame
        select_cover_button = tk.Button(col1_frame, text="Select Cover Image", command=self.select_cover_image)
        select_cover_button.grid(row=1, column=0, padx=5, pady=5)
        select_file_button = tk.Button(col1_frame, text="Select File to Encode", command=self.select_file_to_encode)
        select_file_button.grid(row=2, column=0, padx=5, pady=5)
        encode_button = tk.Button(col1_frame, text="Encode", command=self.encode)
        encode_button.grid(row=3, column=0, padx=5, pady=5)

        # Column 2 Frame
        col2_frame = tk.Frame(top_frame)
        col2_frame.pack(side="right")

        # Image Canvas in Column 2 Frame
        self.image_canvas_col2 = tk.Canvas(col2_frame, width=300, height=200, bg="white")
        self.image_canvas_col2.grid(row=0, column=0, pady=10)
        self.image_canvas_col2.create_image(150, 100, image=self.placeholder_photo)

        # Select image for Decoding
        select_file_button = tk.Button(col2_frame, text="Select File to Decode", command=self.select_file_to_decode)
        select_file_button.grid(row=1, column=0, padx=5, pady=5)

        # Decode Button in Column 2 Frame
        decode_button = tk.Button(col2_frame, text="Decode", command=self.decode)
        decode_button.grid(row=2, column=0, padx=5, pady=5)

        # Empty label for aesthetics
        label = tk.Label(col2_frame, text="")
        label.grid(row=3, column=0, padx=5, pady=6)

        # Bottom Frame
        bottom_frame = tk.Frame(main_frame, bd=2, relief="raised")
        bottom_frame.pack(side="bottom", fill="x", pady=50, padx=30)

        # Buttons in Bottom Frame
        encrypt_folder_button = tk.Button(bottom_frame, text="Encrypt Folder", command=self.encrypt_folder)
        encrypt_folder_button.grid(row=0, column=0, padx=25, pady=5)
        decrypt_folder_button = tk.Button(bottom_frame, text="Decrypt Folder", command=self.decrypt_folder)
        decrypt_folder_button.grid(row=0, column=1, padx=25, pady=5)
        add_file_button = tk.Button(bottom_frame, text="Add File to Database", command=self.add_file_to_database)
        add_file_button.grid(row=0, column=2, padx=25, pady=5)
        file_purge_button = tk.Button(bottom_frame, text="File Purge", command=self.file_purge)
        file_purge_button.grid(row=0, column=3, padx=35, pady=5)

    def select_cover_image(self):
        self.cover_image_file_path = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("Image files", "*.png")])
        if self.cover_image_file_path:
            self.display_image(self.image_canvas_col1, self.cover_image_file_path)
            messagebox.showinfo("Notification", "Cover image selected:\n {} \n\nSelect a file to encode data!".format(self.cover_image_file_path))
            #print("Cover image path: ", self.cover_image_file_path)

    def select_file_to_encode(self):
        self.to_hide_file_path = filedialog.askopenfilename(title="Select File to Encode", filetypes=[("All files", "*.*")])
        if self.to_hide_file_path:
            # Check if file size exceeds the limit
            if os.path.getsize(self.to_hide_file_path) > MAX_FILE_SIZE:
                messagebox.showerror("Error", "File size exceeds the maximum allowed size (2 MB).")
            else:
                # Perform encryption or any other actions here
                messagebox.showinfo("Notification", "File selected:\n {} \n\nClick Encode to begin encoding!".format(self.to_hide_file_path))
                #print("File selected for encryption:", self.to_hide_file_path)

    def encode(self):
        if hasattr(self, 'cover_image_file_path') and hasattr(self, 'to_hide_file_path'):
            imghide.encode_faster(self.cover_image_file_path, self.to_hide_file_path, "output_image.png")
            messagebox.showinfo("Notification", "Encoding Complete!")
        else:
            messagebox.showerror("Error", "Please select a cover image and a file to encode first.")

    def select_file_to_decode(self):
        self.to_unhide_file_path = filedialog.askopenfilename(title="Select File to Decode", filetypes=[("All files", "*.png")])
        if self.to_unhide_file_path:
            self.display_image(self.image_canvas_col2, self.to_unhide_file_path)
            # Perform encryption or any other actions here
            messagebox.showinfo("Notification", "File selected:\n {} \n\nClick Encode to begin encoding!".format(self.to_unhide_file_path))
            #print("File selected for encryption:", self.to_hide_file_path)

    def decode(self):
        if hasattr(self, 'to_unhide_file_path'):
            imghide.decode_faster(self.to_unhide_file_path)
            messagebox.showinfo("Notification", "Decoding Complete!")
        else:
            messagebox.showerror("Error")

    def encrypt_folder(self):
        self.directory_path = filedialog.askdirectory(title="Select Directory to encrypt")
        if self.directory_path:
            imghide.encryptFolder(self.directory_path)
            messagebox.showinfo("Status", "Directory Encrypted!")

    def decrypt_folder(self):
        self.encrypted_directory_path = filedialog.askdirectory(title="Select Directory to decrypt")
        if self.encrypted_directory_path:
            imghide.decryptFolder(self.encrypted_directory_path)
            messagebox.showinfo("Status", "Directory Decrypted!")


    def add_file_to_database(self):
        # Perform adding file to database
        pass

    def file_purge(self):
        self.to_purge_file_path = filedialog.askopenfilename(title="Select File to Purge", filetypes=[("All files", "*.*")])
        if self.to_purge_file_path:
            imghide.shred_file(self.to_purge_file_path)
            messagebox.showinfo("Status", "File Purged Successfully!")

    def display_image(self, canvas, file_path):
        image = Image.open(file_path)
        image = image.resize((300, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(150, 100, image=photo)
        canvas.photo = photo

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
