import ctypes
import math
import multiprocessing
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def init(shared_data, output_data, key, iv, block_size):
    multiprocessing.shared_data = shared_data
    multiprocessing.output_data = output_data
    multiprocessing.key = key
    multiprocessing.iv = iv
    multiprocessing.block_size = block_size

def mapper(blocks):
    ciphertext = multiprocessing.shared_data
    plaintext = multiprocessing.output_data
    block_size = multiprocessing.block_size
    key = multiprocessing.key
    iv = multiprocessing.iv
    cipher = DES.new(key, DES.MODE_ECB)
    cipher.block_size = block_size
    for i in blocks:
        block_begin = i * block_size
        block_end = block_begin + block_size
        block_output = cipher.decrypt(bytes(ciphertext[block_begin:block_end]))
        if i == 0:
            prev = iv
        else:
            prev = bytes(ciphertext[block_begin-block_size:block_begin])
        xored = byte_xor(block_output, prev)
        plaintext[block_begin:block_end] = xored

def decrypt_CBC_par(key: bytes, ciphertext: bytes, iv: bytes, workers_no=4, block_size=8):
    assert len(iv) == block_size
    assert len(ciphertext) % block_size == 0
    blocks_no = int(len(ciphertext) / block_size)
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, ciphertext)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(ciphertext))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, iv, block_size))
    pool.map(mapper, blocks)
    decrypted = unpad(bytes(output_data), block_size)
    return decrypted

if __name__ == '__main__':
    with open('ciphertext', 'rb') as f:
        ciphertext = f.read()
    key = b'haslo123'
    iv  = b'secretiv'
    plaintext = decrypt_CBC_par(key, ciphertext, iv)
    print(plaintext)