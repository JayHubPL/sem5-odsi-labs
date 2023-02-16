import ctypes
import math
import multiprocessing
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def init(shared_data, output_data, key, nonce, work_block_size):
    multiprocessing.shared_data = shared_data
    multiprocessing.output_data = output_data
    multiprocessing.key = key
    multiprocessing.nonce = nonce
    multiprocessing.work_block_size = work_block_size

def encrypt_mapper(blocks):
    plain_text = multiprocessing.shared_data
    cipher_text = multiprocessing.output_data
    key = multiprocessing.key
    nonce = multiprocessing.nonce
    work_block_size = multiprocessing.work_block_size
    for i in blocks:
        block_begin = i * work_block_size
        block_end = min(block_begin + work_block_size, len(plain_text))
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=i)
        curr_ct = cipher.encrypt(bytes(plain_text[block_begin:block_end]))
        cipher_text[block_begin:block_end] = curr_ct
        
def encrypt_CTR_par(key, plain_text, nonce, workers_no, work_block_size):
    plain_text = pad(plain_text, AES.block_size)
    blocks_no = math.ceil(len(plain_text) / work_block_size)
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, plain_text)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(plain_text))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, nonce, work_block_size))
    pool.map(encrypt_mapper, blocks)
    cipher_text = bytes(output_data)
    return cipher_text

def decrypt_mapper(blocks):
    cipher_text = multiprocessing.shared_data
    plain_text = multiprocessing.output_data
    key = multiprocessing.key
    nonce = multiprocessing.nonce
    work_block_size = multiprocessing.work_block_size
    for i in blocks:
        block_begin = i * work_block_size
        block_end = min(block_begin + work_block_size, len(cipher_text))
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=i)
        curr_pt = cipher.decrypt(bytes(cipher_text[block_begin:block_end]))
        plain_text[block_begin:block_end] = curr_pt

def decrypt_CTR_par(key, cipher_text, nonce, workers_no, work_block_size):
    blocks_no = math.ceil(len(cipher_text) / work_block_size)
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, cipher_text)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(cipher_text))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, nonce, work_block_size))
    pool.map(decrypt_mapper, blocks)
    decrypted = unpad(bytes(output_data), AES.block_size)
    return decrypted

def test_decrypt_time(key, cipher_text, nonce, workers_no, work_block_size):
    starttime = time.time()
    decrypted = decrypt_CTR_par(key, cipher_text, nonce, workers_no, work_block_size)
    assert decrypted == plain_text
    return time.time() - starttime

if __name__ == '__main__':
    key = b'haslo123'*2
    plain_text = b'alamakot'*10000
    nonce = b'nonce'
    work_block_size = 128
    cipher_text = encrypt_CTR_par(key, plain_text, nonce, 4, work_block_size)
    with open('ciphertext', 'wb') as f:
        f.write(cipher_text)
    print('-- Benchmark --')
    for W in [1, 2, 4]:
        print(f'AES CTR parallel W = {W}\ttime: {test_decrypt_time(key, cipher_text, nonce, W, work_block_size)}')