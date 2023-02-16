from math import log2
from sys import argv

fname = argv[1]
f = open(fname, "br")
data = f.read()

N = len(data)
n = {}

for b in data:
    if b <= 0xff:
        if b in n:
            n[b] = n[b] + 1
        else:
            n[b] = 1

entropy = 0
for b in n.keys():
    p = n[b] / N
    entropy -= p * log2(p)

print(entropy)