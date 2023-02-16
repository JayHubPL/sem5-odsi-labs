from Crypto.Cipher import ARC4

cipher = ARC4.new(b'foobar')
encrypted = cipher.encrypt(b'tekst')
print(encrypted)