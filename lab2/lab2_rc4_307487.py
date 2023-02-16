import itertools
from math import log2
from string import ascii_lowercase
from Crypto.Cipher import ARC4
from sys import argv

def entropy(bytes):
    N = len(bytes)
    n = {}
    for b in bytes:
        if b <= 0xff:
            if b in n:
                n[b] = n[b] + 1
            else:
                n[b] = 1
    entropy = 0
    for b in n.keys():
        p = n[b] / N
        entropy -= p * log2(p)
    return entropy

class MyRC4:

    def __init__(self, key):
        self.key = key
        self.S = [0] * 256
        for i in range(0, 256):
            self.S[i] = i
        j = 0
        for i in range(0, 256):
            j = (j + self.S[i] + self.key[i % len(self.key)]) % 256
            self.S[i], self.S[j] = self.S[j], self.S[i] # swap

    def encrypt(self, msg):
        encrypted = bytearray(len(msg))
        a = 0
        b = 0
        for (i, byte) in enumerate(msg):
            a = (a + 1) % 256
            b = (b + self.S[a]) % 256
            self.S[a], self.S[b] = self.S[b], self.S[a] # swap
            encrypted[i] = byte ^ self.S[(self.S[a] + self.S[b]) % 256]
        return bytes(encrypted)   

ARC4.key_size = range(3, 257)
fname = argv[1]
f = open(fname, "br")
data = f.read()
treshold = 6

for key in list(map(lambda t: ''.join(t).encode(), itertools.product(ascii_lowercase, repeat=3))):
    cipher = ARC4.new(key)
    decrypted = cipher.decrypt(data)
    if entropy(decrypted) < treshold:
        print(decrypted)
        print("Key: " + str(key))
        break

print("Cryptodome ARC4:")
print(ARC4.new(b'foobar').encrypt(b'random text'))
print("My ARC4 implementation:")
print(MyRC4(b'foobar').encrypt(b'random text'))

