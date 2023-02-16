# Author: Hubert Mazur
# Lab 3

from itertools import product
from math import log2
from string import ascii_lowercase

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from PIL import Image


def entropy(data):
    N = len(data)
    n = {}
    for b in data:
        if b in n:
            n[b] = n[b] + 1
        else:
            n[b] = 1
    entropy = 0
    for b in n.keys():
        p = n[b] / N
        entropy -= p * log2(p)
    return entropy

def nullpadding(data, length=16):
    return data + b"\x00"*(length-len(data) % length) 
 
def convert_to_RGB(data):
    pixels = []
    for i in range(0, len(data) - 1, 3):
        r = int(data[i])
        g = int(data[i+1])
        b = int(data[i+2])
        pixels.append((r,g,b))
    return pixels

def encrypt_full(input_filename, mode, key):
    # read and apply padding to data
    img_in = open(input_filename, "rb")
    data = img_in.read()
    data_padded = nullpadding(data)
    # encrypt data
    aes = initialize_aes(key, mode)
    encrypted_data = aes.encrypt(data_padded)
    encrypted_data_unpadded = encrypted_data[:len(data)]
    # save encrypted image
    (output_filename, _) = prep_output_filename(input_filename, mode, True)
    img_out = open(output_filename, "wb")
    img_out.write(encrypted_data_unpadded)
    img_out.close()
    img_in.close()

def encrypt_data(input_filename, mode, key):
    # read and apply padding to data
    img_in = Image.open(input_filename)
    data = img_in.convert("RGB").tobytes() 
    data_padded = nullpadding(data)
    # encrypt data
    aes = initialize_aes(key, mode)
    encrypted_data = aes.encrypt(data_padded)
    encrypted_data_unpadded = encrypted_data[:len(data)]
    # provides entropy info
    print(mode + ": " + str(entropy(encrypted_data_unpadded))) 
    # save encrypted image
    img_out = Image.new(img_in.mode, img_in.size)
    img_out.putdata(convert_to_RGB(encrypted_data_unpadded))
    (output_filename, img_format) = prep_output_filename(input_filename, mode, True)
    img_out.save(output_filename, img_format)

def decrypt_full(data, mode, key, iv):
    # apply padding
    data_padded = nullpadding(data)
    # decrypt data
    aes = initialize_aes(key, mode, iv)
    decrypted_data = aes.decrypt(data_padded)
    # remove padding
    decrypted_data_unpadded = decrypted_data[:len(data)]
    return decrypted_data_unpadded

def is_bmp_header(header):
    # check if first two bytes match with the BMP header
    return (header[:2] == b'BM')

def prep_output_filename(input_filename, mode, isEncrypted):
    name = ''.join(input_filename.split('.')[:-1])
    format = str(input_filename.split('.')[-1])
    if isEncrypted:
        encryption_info = 'encrypted'
    else:
        encryption_info = 'decrypted'
    output_filename = name + '_' + mode + '_' + encryption_info + '.' + format
    return (output_filename, format)

def initialize_aes(key, mode, iv=None):
    if mode == "CBC":
        if iv == None:
            iv = get_random_bytes(16)
        aes = AES.new(key, AES.MODE_CBC, iv)
    elif mode == "ECB":
        aes = AES.new(key, AES.MODE_ECB)
    return aes

# entropy comparison
demo_img_name = "demo24.bmp"
password = "password"
salt = b"abc"
key = PBKDF2(password, salt, 16)
encrypt_data(demo_img_name, "CBC", key)
encrypt_data(demo_img_name, "ECB", key)

# brute force decrypt 
mode = "CBC"
iv = b'a' * 16
input_filename = "we800_CBC_encrypted_full.bmp"
img_in = open(input_filename, "rb")
input_data = img_in.read()
img_in.close()
# for every password matching pattern [a-z]{3}
for password in list(map(lambda t: ''.join(t), product(ascii_lowercase, repeat=3))):
    # generate key based on the password with a length of 16 bytes
    key = PBKDF2(password, salt, 16)
    # attempt decryption
    decrypted = decrypt_full(input_data, mode, key, iv)
    # check if file header is BMP
    if is_bmp_header(decrypted[:14]):
        # found possible bitmap
        print("Password found: " + password)
        # save decrypted image
        (output_filename, _) = prep_output_filename(input_filename, mode, False)
        img_out = open(output_filename, "wb")
        img_out.write(decrypted)
        img_out.close()
        break
