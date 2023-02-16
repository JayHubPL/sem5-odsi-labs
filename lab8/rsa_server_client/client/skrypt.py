from client import Client
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

server_url = "http://10.65.1.44:5000"
c1_pub_key = open('keys/c1.pub', 'rb').read()
c2_pub_key = open('keys/c2.pub', 'rb').read()
c1_priv_key = RSA.import_key(open('keys/c1', 'rb').read())
c2_priv_key = RSA.import_key(open('keys/c2', 'rb').read())

c1 = Client(server_url)
c2 = Client(server_url)
c1.send_key('c1', c1_pub_key)
c2.send_key('c2', c2_pub_key)

# Zadanie 1
# Wysłać poprawnie zaszyfrowaną wiadomość do użytkownika deadbeef

deadbeef_pub_key = RSA.import_key(c1.get_key('deadbeef'))
message = b'Hello deadbeef!'
cipher = PKCS1_OAEP.new(deadbeef_pub_key)
encrypted_message = cipher.encrypt(message)
c1.send_binary_message('deadbeef', encrypted_message)

# Zadanie 2
# Proszę przeprowadzić szyfrowaną komunikację w obu kierunkach między dwoma stworzonymi użytkownikami.

# C1 wysyła wiadomość do C2
c2_pub_key = RSA.import_key(c1.get_key('c2'))
message = b'Hi C2, it is me, C1!'
cipher = PKCS1_OAEP.new(c2_pub_key)
encrypted_message = cipher.encrypt(message)
c1.send_binary_message('c2', encrypted_message) # Wiadomość trafiła na serwer ale jest zaszyfrowana

# C2 odszyfrowuje wiadomość od C1
encrypted_message = base64.decodebytes(c2.get_text_message('c2').encode('utf-8'))
decipher = PKCS1_OAEP.new(c2_priv_key)
decrypted_message = decipher.decrypt(encrypted_message)
print(decrypted_message)

# C2 wysyła wiadomość do C1
c1_pub_key = RSA.import_key(c2.get_key('c1'))
message = b'Hi C1, it is me, C2!'
cipher = PKCS1_OAEP.new(c1_pub_key)
encrypted_message = cipher.encrypt(message)
c1.send_binary_message('c1', encrypted_message) # Wiadomość trafiła na serwer ale jest zaszyfrowana

# C1 odszyfrowuje wiadomość od C2
c2_pub_key = RSA.import_key(c1.get_key('c2'))
encrypted_message = base64.decodebytes(c1.get_text_message('c1').encode('utf-8'))
decipher = PKCS1_OAEP.new(c1_priv_key)
decrypted_message = decipher.decrypt(encrypted_message)
print(decrypted_message)

# Zadanie 3
# Proszę przeprowadzić szyfrowaną komunikację w obu kierunkach między dwoma stworzonymi użytkownikami z wykorzystaniem podpisów

# C1 wysyła wiadomość z podpisem do C2
c2_pub_key = RSA.import_key(c1.get_key('c2'))
message = b'Hello C2!'
sig = pkcs1_15.new(c1_priv_key).sign(SHA256.new(message))
encrypted_message = PKCS1_OAEP.new(c2_pub_key).encrypt(message)
c1.send_binary_signed_message('c2', encrypted_message, sig)

# C2 odszyfrowuje podpisaną wiadomość od C1
c1_pub_key = RSA.import_key(c2.get_key('c1'))
encrypted_message, sig = c2.get_signed_text_message('c2')
decrypted_message = PKCS1_OAEP.new(c2_priv_key).decrypt(encrypted_message)
print(f'Message: {decrypted_message}')
try:
    pkcs1_15.new(c1_pub_key).verify(SHA256.new(decrypted_message), sig)
    print('Tożsamość C1 potwierdzona!')
except (ValueError, TypeError):
    print('Tożsamość nadawcy nie została potwierdzona!')