import base64
import json
import os
import LSBSteg
import cv2
import crypto

PASSWORD = "Ac2$/v}n5{M?LqNGurUmtzb:j>Qs`9@."

def fileTob85(filepath):
    with open(filepath, "rb") as file:
        fileContent = file.read()
        fileName = filepath.split("/")[-1]
        bsf_buffer = {
            "file_name": fileName,
            "file_content": base64.b85encode(fileContent).decode('utf-8')
        }
    file.close()
    encoded_buffer = json.dumps(bsf_buffer)
    return encoded_buffer

def b85toFile(dataStream):
    stringify_bsf_buffer = json.loads(dataStream)
    file_content = base64.b85decode(stringify_bsf_buffer['file_content'])
    file_name = stringify_bsf_buffer['file_name']
    file_path = f"output/{file_name}"
    if not os.path.exists("output"):
        os.makedirs("output")
    with open(file_path, 'wb') as file:
        file.write(file_content)

def decode_faster(filePath):
    steg = LSBSteg.LSBSteg(cv2.imread(filePath))
    binary = steg.decode_binary()
    b85toFile(binary)
    print("Decoding Successfull!!")

def encode_faster(coverImage, filePath, destPath):
    steg = LSBSteg.LSBSteg(cv2.imread(coverImage))
    data = fileTob85(filePath)
    stegoImage = steg.encode_binary(data)
    cv2.imwrite(destPath, stegoImage)   
    print("Encoding Successfull!!")

def shred_file(file_path):
    with open(file_path, 'wb') as f:
        file_size = os.path.getsize(file_path)
        for _ in range(10):
            f.seek(0)
            f.write(os.urandom(file_size))

            # uncomment the below line if you know what you are doing !!!
            #f.flush()

    os.remove(file_path)

def encryptFolder(folderpath):
    for file in os.listdir(folderpath):
        crypto.encryptFile(folderpath+"/"+file, f"{folderpath}/{file}.shdx", PASSWORD)
        print(f"Encypted {file} with Password!")
        shred_file(folderpath+"/"+file)

def decryptFolder(folderpath):
    for file in os.listdir(folderpath):
        if file.lower().endswith(".shdx"):
            crypto.decryptFile(folderpath+"/"+file, (folderpath+"/"+file).replace(".shdx", ""), PASSWORD)
            print(f"File {file} Decrypted")
            shred_file(folderpath+"/"+file)
