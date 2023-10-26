from flask import Flask
from os.path import exists

import views.RevProxy
from views.ServiceWorker import management
from views.RevProxy import meter_management
from GlobalStorage import export_meters, import_meters

import logging
import atexit
import threading

app = Flask(__name__)

app.register_blueprint(management, url_prefix="/service-worker")
app.register_blueprint(meter_management, url_prefix="/meter")


def start_server():
    if exists("data.pickle"):
        # TODO load old data
        pass
    logging.info("Start webserver")


def stop_server():
    # TODO save meters for persistence
    pass


logging.basicConfig(filename="./log.txt", encoding="UTF-8", format='%(asctime)s %(levelname)s:%(message)s',
                    filemode="w", level=logging.INFO)
atexit.register(stop_server)

notifier_thread = threading.Thread(target=views.RevProxy.send_meters, args=[])
notifier_thread.start()
start_server()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=25565)
