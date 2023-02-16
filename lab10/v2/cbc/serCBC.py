from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def encrypt_CBC_serial(key: bytes, plaintext: bytes, iv: bytes, block_size=8) -> bytes:
    assert len(iv) == block_size
    cipher = DES.new(key, DES.MODE_ECB)
    cipher.block_size = block_size
    padded = pad(plaintext, block_size)
    blocks_no = int(len(padded) / block_size)
    ciphertext = bytearray(len(padded))
    for i in range(blocks_no):
        block_begin = i * block_size
        block_end = block_begin + block_size
        if i == 0:
            prev = iv
        else:
            prev = ciphertext[block_begin-block_size:block_begin]
        xored = byte_xor(padded[block_begin:block_end], prev)
        ciphertext[block_begin:block_end] = cipher.encrypt(xored)
    return bytes(ciphertext)

if __name__ == '__main__':
    key = b'haslo123'
    iv  = b'secretiv'
    plaintext = b'alamakota' * 3
    ciphertext = encrypt_CBC_serial(key, plaintext, iv)
    with open('ciphertext', 'wb') as f:
        f.write(ciphertext)
    print(ciphertext)