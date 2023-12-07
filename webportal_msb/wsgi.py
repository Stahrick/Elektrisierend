import ssl

from web_server import app

if __name__ == "__main__":
    context = ('localhost.crt', 'localhost.key')
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=context[0])
    ssl_context.load_cert_chain(certfile=context[0], keyfile=context[1], password=None)
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(ssl_context=ssl_context)