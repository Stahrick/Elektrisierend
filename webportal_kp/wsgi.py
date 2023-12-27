import ssl
from config import mycert, root_ca
from web_server import app, PeerCertWSGIRequestHandler

if __name__ == "__main__":
    context = mycert
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=root_ca)
    ssl_context.load_cert_chain(certfile=context[0], keyfile=context[1], password=None)
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(host='0.0.0.0', port=4000, debug=False, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)