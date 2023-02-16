from sys import argv

fname = argv[1]
f = open(fname, "r")
text = f.read().rstrip().lower()

n = {}
for character in text:
    if character in n:
        n[character] = n[character] + 1
    else:
        n[character] = 1

for character in n.keys():
    print(character + " => " + str(n[character]))
