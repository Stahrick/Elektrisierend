from os import urandom

COOKIE_SIGN_KEY = urandom(16)
MSB_URL = "https://127.0.0.1:5000/meter"
mycert = ('localhost.crt', 'localhost.key')
root_ca = 'RootCA.crt'