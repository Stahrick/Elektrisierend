from os import urandom

COOKIE_SIGN_KEY = urandom(16)
MSB_URL = "http://127.0.0.1:5000/meter"