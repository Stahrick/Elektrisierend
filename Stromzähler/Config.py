from os import urandom

cookie_sign_key = urandom(16)
msb_url = "http://127.0.0.1:5000/meter"