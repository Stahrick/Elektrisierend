from os import urandom

COOKIE_SIGN_KEY = urandom(16)
MSB_URL = "https://localhost:5000/meter"
mycert = ('localhost.crt', 'localhost.key')
root_ca = 'RootCA.crt'