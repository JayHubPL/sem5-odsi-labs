from logging import error
from passlib.hash import argon2, md5_crypt, sha256_crypt, bcrypt
from itertools import product, count
from string import ascii_letters, ascii_lowercase
from time import time
from hashlib import sha256
from base64 import b64decode

def measure_hash_time(hash_fun, n=1000, password_len=6):
    password_iter = map(lambda t: ''.join(t).encode('ascii'), product(ascii_lowercase, repeat=password_len))
    start_time = time()
    for _ in range(n):
        password = next(password_iter)
        if hash_fun == 'argon2':
            argon2.hash(password)
        elif hash_fun == 'md5':
            md5_crypt.hash(password)
        elif hash_fun == 'sha256':
            sha256(password)
        elif hash_fun == 'bcrypt':
            bcrypt.hash(password)
        else:
            error('Unimplemented hash funcion')
    finish_time = time()
    average_time = (finish_time - start_time) / n
    print(f"{hash_fun}: {average_time}")
    return average_time
    
def find_collision_sha256():
    hash_set = set()
    tries = 0
    for dock_len in count(1):
        dock_iter = map(lambda t: ''.join(t), product(ascii_letters, repeat=dock_len))
        while (dock := next(dock_iter, None)) is not None:
            tries += 1
            hash = sha256(dock.encode('ascii')).hexdigest()[:10]
            if (hash in hash_set):
                print(f'Matching hash beginning found \'{hash}\' after {tries} tries.')
                return
            hash_set.add(hash)

def break_argon_hash():
    hash_to_match = '$argon2id$v=19$m=65536,t=3,p=4$4Vzr3bvXWuvdmzMG4PxfCw$NWNunMWdo0ugkWWsL8Z+sdMKnDcJp0vDfMkr30Lmpd4'
    salt = b64decode('4Vzr3bvXWuvdmzMG4PxfCw==')
    argon = argon2(type='ID', version=19, memory_cost=65536, rounds=3, parallelism=4, salt=salt)
    iter = map(lambda t: ''.join(t), product(ascii_lowercase, repeat=2))
    while (password := next(iter, None)) is not None:
        hash = argon.using(salt=salt).hash(password)
        if (hash == hash_to_match):
            print(f'Password: {password}')
            break

def main():
    # Time comparison for hash functions
    measure_hash_time('argon2')                 # argon2:           0.054840495824813845
    measure_hash_time('md5')                    # md5:              0.0009534368515014648
    sha256_time = measure_hash_time('sha256')   # (hashlib)sha256:  8.039474487304687e-07
    measure_hash_time('bcrypt')                 # bcrypt:           0.2210385992527008


    # How much time to break [a-z]{6} password?
    # Macs use SHA-512 to get password hashes and despite the fact that SHA-512
    # has 25% more rounds than SHA-256 on a 64-bit processor each round takes
    # the same amount of operations, yet can process double the data per round,
    # because the instructions process 64-bit words instead of 32-bit words.
    # Therefore, 2 / 1.25 = 1.6, which is how much faster SHA-512 can be under
    # optimal conditions.
    # https://crypto.stackexchange.com/questions/26336/sha-512-faster-than-sha-256
    print(f'{round((sha256_time / 1.5) * (len(ascii_lowercase) ** 6) / 60)} minutes')

    # Collision finder
    find_collision_sha256()
    # Example:
    # Matching hash beginning found 'abe9e0a87d' after 1147040 tries.

    # Break argon2 hash
    # https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html#format-algorithm
    break_argon_hash()
    # Password: wc