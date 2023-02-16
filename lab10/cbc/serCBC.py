from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

def encrypt_CBC_serial(key, plain_text, iv):
    plain_text = pad(plain_text, DES.block_size)
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    cipher_text = cipher.encrypt(plain_text)
    return cipher_text

if __name__ == '__main__':
    key = b'haslo123'
    iv = b'12345678'
    plain_text = b'alamakot'*10000
    cipher_text = encrypt_CBC_serial(key, plain_text, iv)
    print(cipher_text)
    with open('ciphertext', 'wb') as f:
	    f.write(cipher_text)
