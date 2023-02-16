import ctypes
import multiprocessing
from math import log2, floor
import time
from secrets import token_bytes
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def init(shared_data, output_data, key, nonce, block_size):
    multiprocessing.shared_data = shared_data
    multiprocessing.output_data = output_data
    multiprocessing.key = key
    multiprocessing.nonce = nonce
    multiprocessing.block_size = block_size

def encrypt_mapper(blocks):
    plaintext = multiprocessing.shared_data
    ciphertext = multiprocessing.output_data
    key = multiprocessing.key
    nonce = multiprocessing.nonce
    block_size = multiprocessing.block_size
    cipher = DES.new(key, DES.MODE_ECB)
    cipher.block_size = block_size
    for i in blocks:
        block_begin = i * block_size
        block_end = block_begin + block_size
        nonce_ctr = nonce + i.to_bytes(length=block_size-len(nonce), byteorder='little')
        keystream_block = cipher.encrypt(nonce_ctr)
        xored = byte_xor(plaintext[block_begin:block_end], keystream_block)
        ciphertext[block_begin:block_end] = xored


def encrypt_CTR_par(key: bytes, plaintext: bytes, nonce: bytes, workers_no=4, block_size=16) -> bytes:
    plaintext = pad(plaintext, block_size)
    blocks_no = int(len(plaintext) / block_size)
    assert len(nonce) + floor(log2(blocks_no-1)) + 1 <= block_size
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, plaintext)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(plaintext))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, nonce, block_size))
    pool.map(encrypt_mapper, blocks)
    ciphertext = bytes(output_data)
    return ciphertext

def decrypt_mapper(blocks):
    ciphertext = multiprocessing.shared_data
    plaintext = multiprocessing.output_data
    key = multiprocessing.key
    nonce = multiprocessing.nonce
    block_size = multiprocessing.block_size
    cipher = DES.new(key, DES.MODE_ECB)
    cipher.block_size = block_size
    for i in blocks:
        block_begin = i * block_size
        block_end = block_begin + block_size
        nonce_ctr = nonce + i.to_bytes(length=block_size-len(nonce), byteorder='little')
        keystream_block = cipher.encrypt(nonce_ctr)
        xored = byte_xor(ciphertext[block_begin:block_end], keystream_block)
        plaintext[block_begin:block_end] = xored

def decrypt_CTR_par(key: bytes, ciphertext: bytes, nonce: bytes, workers_no=4, block_size=16) -> bytes:
    assert len(ciphertext) % block_size == 0
    blocks_no = int(len(ciphertext) / block_size)
    assert len(nonce) + floor(log2(blocks_no-1)) + 1 <= block_size
    blocks = [range(i, blocks_no, workers_no) for i in range(workers_no)]
    shared_data = multiprocessing.RawArray(ctypes.c_ubyte, ciphertext)
    output_data = multiprocessing.RawArray(ctypes.c_ubyte, len(ciphertext))
    pool = multiprocessing.Pool(workers_no, initializer=init, initargs=(shared_data, output_data, key, nonce, block_size))
    pool.map(decrypt_mapper, blocks)
    decrypted = unpad(bytes(output_data), block_size)
    return decrypted

def test_decrypt_time(key, plaintext, ciphertext, nonce, workers_no, block_size=16):
    starttime = time.time()
    decrypted = decrypt_CTR_par(key, ciphertext, nonce, workers_no, block_size)
    assert decrypted == plaintext
    return time.time() - starttime

if __name__ == '__main__':
    key = b'haslo123'
    nonce  = token_bytes(5)
    plaintext = b'alamakota' * 2000
    ciphertext = encrypt_CTR_par(key, plaintext, nonce)
    print('------- BENCHMARK -------')
    for W in [1, 2, 4]:
        print(f'DES CTR parallel W = {W}\ttime: {test_decrypt_time(key, plaintext, ciphertext, nonce, W)}')