import io
import warnings
from os import path, remove, urandom

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# default encryption/decryption buffer size - 64KB
bufferSizeDef = 128 * 1024

# maximum password length (number of chars)
maxPassLen = 1024

# AES block size in bytes
AESBlockSize = 16


# password stretching function
def stretch(passw, iv1):

    # hash the external iv and the password 8192 times
    digest = iv1 + (16 * b"\x00")

    for i in range(8192):
        passHash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        passHash.update(digest)
        passHash.update(bytes(passw, "utf_16_le"))
        digest = passHash.finalize()

    return digest

def encryptFile(infile, outfile, passw, bufferSize=bufferSizeDef):
    try:
        with open(infile, "rb") as fIn:
            # check that output file does not exist
            # or that, if exists, is not the same as the input file
            # (i.e.: overwrite if it seems safe)
            if path.isfile(outfile):
                if path.samefile(infile, outfile):
                    raise ValueError("Input and output files are the same.")
            try:
                with open(outfile, "wb") as fOut:
                    # encrypt file stream
                    encryptStream(fIn, fOut, passw, bufferSize)

            except IOError:
                raise ValueError("Unable to write output file.")

    except IOError:
        raise ValueError("Unable to read input file.")


def encryptStream(fIn, fOut, passw, bufferSize=bufferSizeDef):
    # validate bufferSize
    if bufferSize % AESBlockSize != 0:
        raise ValueError("Buffer size must be a multiple of AES block size.")

    if len(passw) > maxPassLen:
        raise ValueError("Password is too long.")

    # generate external iv (used to encrypt the main iv and the
    # encryption key)
    iv1 = urandom(AESBlockSize)

    # stretch password and iv
    key = stretch(passw, iv1)

    # generate random main iv
    iv0 = urandom(AESBlockSize)

    # generate random internal key
    intKey = urandom(32)

    # instantiate AES cipher
    cipher0 = Cipher(algorithms.AES(intKey), modes.CBC(iv0), backend=default_backend())
    encryptor0 = cipher0.encryptor()

    # instantiate HMAC-SHA256 for the ciphertext
    hmac0 = hmac.HMAC(intKey, hashes.SHA256(), backend=default_backend())

    # instantiate another AES cipher
    cipher1 = Cipher(algorithms.AES(key), modes.CBC(iv1), backend=default_backend())
    encryptor1 = cipher1.encryptor()

    # encrypt main iv and key
    c_iv_key = encryptor1.update(iv0 + intKey) + encryptor1.finalize()

    # calculate HMAC-SHA256 of the encrypted iv and key
    hmac1 = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    hmac1.update(c_iv_key)

    # write header
    fOut.write(bytes("AES", "utf8"))

    fOut.write(b"\x02")

    # reserved byte (set to zero)
    fOut.write(b"\x00")

    # setup "CREATED-BY" extension
    cby = "SHIDEX-TEAM3 "

    # write "CREATED-BY" extension length
    fOut.write(b"\x00" + bytes([1 + len("ENCRYPTED_BY" + cby)]))

    # write "CREATED-BY" extension
    fOut.write(bytes("ENCRYPTED_BY", "utf8") + b"\x00" + bytes(cby, "utf8"))

    # write "container" extension length
    fOut.write(b"\x00\x80")

    # write "container" extension
    for i in range(128):
        fOut.write(b"\x00")

    # write end-of-extensions tag
    fOut.write(b"\x00\x00")

    # write the iv used to encrypt the main iv and the
    # encryption key
    fOut.write(iv1)

    # write encrypted main iv and key
    fOut.write(c_iv_key)

    # write HMAC-SHA256 of the encrypted iv and key
    fOut.write(hmac1.finalize())

    # encrypt file while reading it
    while True:
        # try to read bufferSize bytes
        fdata = fIn.read(bufferSize)

        # get the real number of bytes read
        bytesRead = len(fdata)

        # check if EOF was reached
        if bytesRead < bufferSize:
            # file size mod 16, lsb positions
            fs16 = bytes([bytesRead % AESBlockSize])
            # pad data 
            if bytesRead % AESBlockSize == 0:
                padLen = 0
            else:
                padLen = 16 - bytesRead % AESBlockSize
            fdata += bytes([padLen]) * padLen
            # encrypt data
            cText = encryptor0.update(fdata) + encryptor0.finalize()
            # update HMAC
            hmac0.update(cText)
            # write encrypted file content
            fOut.write(cText)
            # break
            break
        else:
            # encrypt data
            cText = encryptor0.update(fdata)
            # update HMAC
            hmac0.update(cText)
            # write encrypted file content
            fOut.write(cText)

    # write plaintext file size mod 16 lsb positions
    fOut.write(fs16)

    # write HMAC-SHA256 of the encrypted file
    fOut.write(hmac0.finalize())

def decryptFile(infile, outfile, passw, bufferSize=bufferSizeDef):
    try:
        with open(infile, "rb") as fIn:
            if path.isfile(outfile):
                if path.samefile(infile, outfile):
                    raise ValueError("Input and output files are the same.")
            try:
                with open(outfile, "wb") as fOut:
                    try:
                        decryptStream(fIn, fOut, passw, bufferSize)
                    except ValueError as exd:
                        raise ValueError(str(exd))

            except IOError:
                raise ValueError("Unable to write output file.")
            except ValueError as exd:
                remove(outfile)
                raise ValueError(str(exd))

    except IOError:
        raise ValueError("Unable to read input file.")

def decryptStream(fIn, fOut, passw, bufferSize=bufferSizeDef, inputLength=None):
    if inputLength is not None:
        warnings.warn(
            "inputLength parameter is no longer used, and might be removed in a future version",
            DeprecationWarning,
            stacklevel=2,
        )
    if bufferSize % AESBlockSize != 0:
        raise ValueError("Buffer size must be a multiple of AES block size")

    if len(passw) > maxPassLen:
        raise ValueError("Password is too long.")

    if not hasattr(fIn, "peek"):
        fIn = io.BufferedReader(getBufferableFileobj(fIn), bufferSize)

    fdata = fIn.read(3)
    if fdata != b"AES":
        raise ValueError("File is corrupted or not a SHIDEX file.")

    fdata = fIn.read(1)
    if len(fdata) != 1:
        raise ValueError("File is corrupted.")

    if fdata != b"\x02":
        raise ValueError(
            "SHIDEX is only compatible with version "
            "2 of the AES Crypt file format."
        )

    # skip reserved byte
    fIn.read(1)

    # skip all the extensions
    while True:
        fdata = fIn.read(2)
        if len(fdata) != 2:
            raise ValueError("File is corrupted.")
        if fdata == b"\x00\x00":
            break
        fIn.read(int.from_bytes(fdata, byteorder="big"))

    # read external iv
    iv1 = fIn.read(16)
    if len(iv1) != 16:
        raise ValueError("File is corrupted.")

    # stretch password and iv
    key = stretch(passw, iv1)

    # read encrypted main iv and key
    c_iv_key = fIn.read(48)
    if len(c_iv_key) != 48:
        raise ValueError("File is corrupted.")

    # read HMAC-SHA256 of the encrypted iv and key
    hmac1 = fIn.read(32)
    if len(hmac1) != 32:
        raise ValueError("File is corrupted.")

    # compute actual HMAC-SHA256 of the encrypted iv and key
    hmac1Act = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    hmac1Act.update(c_iv_key)

    # HMAC check
    if hmac1 != hmac1Act.finalize():
        raise ValueError("Wrong password (or file is corrupted).")

    # instantiate AES cipher
    cipher1 = Cipher(algorithms.AES(key), modes.CBC(iv1), backend=default_backend())
    decryptor1 = cipher1.decryptor()

    # decrypt main iv and key
    iv_key = decryptor1.update(c_iv_key) + decryptor1.finalize()

    # get internal iv and key
    iv0 = iv_key[:16]
    intKey = iv_key[16:]

    # instantiate another AES cipher
    cipher0 = Cipher(algorithms.AES(intKey), modes.CBC(iv0), backend=default_backend())
    decryptor0 = cipher0.decryptor()

    # instantiate actual HMAC-SHA256 of the ciphertext
    hmac0Act = hmac.HMAC(intKey, hashes.SHA256(), backend=default_backend())

    # decrypt ciphertext, until last block is reached
    last_block_reached = False
    while not last_block_reached:
        # read data
        cText = fIn.read(bufferSize)

        # end of buffer
        if len(fIn.peek(32 + 1)) < 32 + 1:
            last_block_reached = True
            cText += fIn.read()
            fs16 = cText[-32 - 1]  # plaintext file size mod 16 lsb positions
            hmac0 = cText[-32:]
            cText = cText[: -32 - 1]

        # update HMAC
        hmac0Act.update(cText)
        # decrypt data and write it to output file
        pText = decryptor0.update(cText)

        # remove padding
        if last_block_reached:
            toremove = (16 - fs16) % 16
            if toremove:
                pText = pText[:-toremove]

        fOut.write(pText)

    # HMAC check
    if hmac0 != hmac0Act.finalize():
        raise ValueError("Bad HMAC (file is corrupted).")

class BufferableFileobj:
    def __init__(self, fileobj):
        self.__fileobj = fileobj
        self.closed = False

    def readable(self):
        return True

    def read(self, n = -1):
        return self.__fileobj.read(n)

    def readinto(self, b):
        rbuf = self.read(len(b))
        n = len(rbuf)
        b[0:n] = rbuf
        return n

def getBufferableFileobj(fileobj):
    noattr = object()
    for attr in ('readable','readinto','closed'):
        if getattr(fileobj, attr, noattr) == noattr:
            return BufferableFileobj(fileobj)
    return fileobj
