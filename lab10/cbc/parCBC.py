import ctypes
import math
import multiprocessing
import time
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad

def init(shared_data, output_data, key, iv, work_block_size):
    multiprocessing.shared_data = shared_data
    multiprocessing.output_data = output_data
    multiprocessing.key = key
    multiprocessing.iv = iv
    multiprocessing.work_block_size = work_block_size

def mapper(blocks):
    cipher_text = multiprocessing.shared_data
    plain_text = multiprocessing.output_data
    work_block_size = multiprocessing.work_block_size
    for i in blocks:
        block_begin = i * work_block_size
        block_end = block_begin + work_block_size
        if i == 0:
            prev_block = multiprocessing.iv
        else:
            prev_block = bytes(cipher_text[block_begin-DES.block_size:block_begin])
        cipher = DES.new(multiprocessing.key, DES.MODE_CBC, iv=prev_block)
        plain_text[block_begin:block_end] = cipher.decrypt(bytes(cipher_text[block_begin:block_end]))

def decrypt_CBC_par(key, cipher_text, iv, workers_no, work_block_size):
    blocks_no = math.ceil(len(cipher_text) / work_block_size)
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, cipher_text)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(cipher_text))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, iv, work_block_size))
    pool.map(mapper, blocks)
    decrypted = unpad(bytes(output_data), DES.block_size)
    return decrypted

def test_decrypt_time(key, cipher_text, iv, workers_no, work_block_size):
    starttime = time.time()
    decrypt_CBC_par(key, cipher_text, iv, workers_no, work_block_size)
    return time.time() - starttime

if __name__ == '__main__':
    with open('ciphertext', 'rb') as f:
        cipher_text = f.read()
    key = b'haslo123'
    iv = b'12345678'
    work_block_size = 128
    decrypted = decrypt_CBC_par(key, cipher_text, iv, 4, work_block_size)
    print(decrypted)
    for W in [1, 2, 4]:
        print(f'AES CTR parallel W = {W}\ttime: {test_decrypt_time(key, cipher_text, iv, W, work_block_size)}')
