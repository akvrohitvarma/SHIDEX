import random
import string

def create_random_file(file_size_mb):
    file_size_bytes = int(file_size_mb * 1024 * 1024)
    
    random_data = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + string.whitespace, k=file_size_bytes))

    random_name = ''.join(random.choices(string.ascii_lowercase, k=4))

    with open(f"testMe/{random_name}.txt", "w") as f:
        f.write(random_data)

    print(f"Random file '{random_name}.txt' with size {file_size_mb} MB created successfully.")

def main():
    try:
        file_size_mb = float(input("Enter the file size in MB: "))
        if file_size_mb <= 0 or file_size_mb > 5:
            print("File size must be greater than zero and less than 5MB.")
            return
        files = input("Enter number of files required [Default: 1]: ")
        if files == "" or files == 1:
            files = 1
        for i in range(0, int(files)):
            create_random_file(file_size_mb)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
