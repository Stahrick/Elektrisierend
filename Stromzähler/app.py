import json
import ssl

import OpenSSL
from flask import Flask
from os.path import exists
from pathlib import Path

import views.RevProxy
from views.ServiceWorker import management
from views.RevProxy import meter_management
from GlobalStorage import export_meters, import_meters
from SmartMeter import Meter

import logging
import atexit
import threading

class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
    """
    We subclass this class so that we can gain access to the connection
    property. self.connection is the underlying client socket. When a TLS
    connection is established, the underlying socket is an instance of
    SSLSocket, which in turn exposes the getpeercert() method.
    The output from that method is what we want to make available elsewhere
    in the application.
    """
    def make_environ(self):
        """
        The superclass method develops the environ hash that eventually
        forms part of the Flask request object.
        We allow the superclass method to run first, then we insert the
        peer certificate into the hash. That exposes it to us later in
        the request variable that Flask provides
        """
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        if x509_binary:
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
            environ['peercert'] = x509
            return environ
        environ['peercert'] = None
        return environ

app = Flask(__name__)

app.register_blueprint(management, url_prefix="/service-worker")
app.register_blueprint(meter_management, url_prefix="/meter")

path = Path(__file__).parent

def start_server():
    if exists(path / "save_meters.json"):
        with open(path / "save_meters.json", "r") as f:
            data = json.load(f)
            meters = {uuid: Meter.from_dict(meter_data) for uuid, meter_data in data.items()}
            import_meters(meters)
            app.logger.info("Loaded old state")
    app.logger.info("Start webserver")


def stop_server():
    with open(path / "save_meters.json", "w") as f:
        json.dump(export_meters(), f)


# logging.basicConfig(filename="./log.txt", encoding="UTF-8", format='%(asctime)s %(levelname)s:%(message)s',
#                    filemode="w", level=logging.DEBUG)

atexit.register(stop_server)

notifier_thread = threading.Thread(target=views.RevProxy.send_meters, args=[])
notifier_thread.daemon = True
notifier_thread.start()
cleaner_thread = threading.Thread(target=views.RevProxy.clean_sessions, args=[])
cleaner_thread.daemon = True
cleaner_thread.start()
start_server()

context = ('localhost.crt', 'localhost.key')
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=context[0] )
ssl_context.load_cert_chain(certfile=context[0], keyfile=context[1], password=None )
ssl_context.verify_mode = ssl.CERT_OPTIONAL
app.run(host='0.0.0.0', port=25565, debug=True, ssl_context=context)
