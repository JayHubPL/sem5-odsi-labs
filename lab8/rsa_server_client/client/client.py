import requests, base64
STATUS_OK = 200

class Client:
  def __init__(self, server_url):
    self.server_url = server_url

  def send_key(self, uid, key):
    url = self.server_url + '/key/' + uid
    data = { 'key' : key.decode() }
    response = requests.post(url, json=data)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')
    print(f'SUCCESS: {response.text}')

  def get_key(self, uid):
    url = self.server_url + '/key/' + uid
    response = requests.get(url)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')

    key = response.text.encode()
    return key

  def send_binary_message(self, uid, msg):
    txt = base64.encodebytes(msg).decode()
    self.send_text_message(uid, txt)

  def send_text_message(self, uid, msg):
    url = self.server_url + '/message/' + uid
    data = { 'message' : msg }
    response = requests.post(url, json=data)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')
    print(f'SUCCESS: {response.text}')

  def get_text_message(self, uid):
    url = self.server_url + '/message/' + uid
    response = requests.get(url)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')

    txt = response.json()['message']
    return txt

  def get_signed_text_message(self, uid):
    url = self.server_url + '/message/' + uid
    response = requests.get(url)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')
    json = response.json()
    message = base64.decodebytes(json['message'].encode('utf-8'))
    sig = base64.decodebytes(json['sig'].encode('utf-8'))
    return message, sig

  def get_binary_message(self, uid):
    txt = self.get_text_message(uid)
    msg = base64.decodebytes(txt.encode())
    return msg

  def send_binary_signed_message(self, receiver_uid, msg, sig):
    msg = base64.encodebytes(msg).decode()
    sig = base64.encodebytes(sig).decode()
    url = self.server_url + '/message/' + receiver_uid
    data = { 'message' : msg, 'sig' : sig }
    response = requests.post(url, json=data)
    if response.status_code != STATUS_OK:
      raise Exception(f'FAIL({response.status_code}): {response.text}')
    print(f'SUCCESS: {response.text}')