import json

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

# if __name__ == "__main__":
app.run(debug=True, port=25565)
