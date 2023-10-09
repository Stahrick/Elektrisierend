import random
import logging
import requests

from datetime import datetime
from flask import make_response
from uuid import uuid4

logging.getLogger(__name__)

average_kwh_per_sec = 2050 / 365 / 24 / 60 / 60  # Average 2050kwh per person per year


class Meter:
    uuid = None
    meter = None
    last_update = None
    maintenance_activation_time = None
    maintainer_cert = None

    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid

    def setup_meter(self, registration_code):
        # TODO Check signature and hash verification
        # Check uuid in registration_code with device uuid
        if self.uuid != registration_code["uuid"]:
            logging.info(f"Invalid registration code provided for device({self.uuid}): {registration_code}")
            return "Invalid registration code provided", 400
        self.meter = random.randrange(0, 50)
        logging.info(f"Initialized meter with {self.meter} KWH")

    def activate_maintenance(self, req):
        self.maintenance_activation_time = datetime.now()
        logging.info(f"Activated maintenance from host {req.host}")

    def set_meter(self, req):
        msg = req.json
        self.meter = msg["Meter"]
        self.last_request = datetime.now()
        logging.info(f"SET meter from host {req.host} to {self.meter}")

    def restart(self):
        # Restart device
        logging.warning("Restart triggered")
        return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)

    def swap_certificate(self, req):
        # Swap the maintainer certificate
        logging.warning("Certificate swap triggered")
        self.maintainer_cert = req.json["Certificate"]
        return make_response("Certificate renewed", 200)

    def send_meter(self):
        global average_kwh_per_sec
        cur_time = datetime.now()
        passed_sec = (cur_time - self.last_update).total_seconds()
        amount_added = random.uniform(average_kwh_per_sec - float("1e-5"), average_kwh_per_sec + float("1e-5"))
        self.meter += passed_sec * amount_added
        # TODO Add url
        requests.post("", {"uuid": self.uuid, "meter": self.meter})
        logging.info(f"SEND meter data {self.meter} Kwh")


    def is_in_maintenance(self):
        cur_time = datetime.now()
        return (self.maintenance_activation_time is not None
                and ((cur_time - self.maintenance_activation_time).total_seconds() / 60) < 5)


def send_meter():
    update_meter()



def set_meter():
    global maintenance_activation_time
    global last_request
    global meter

    cur_time = datetime.now()
    # Check if maintenance mode was activated more than 5 minutes ago
    if maintenance_activation_time is None or ((cur_time - maintenance_activation_time).total_seconds() / 60) > 5:
        logging.warning(f"Try to SET meter from host {request.host}, but failed caused by deactivated maintenance mode")
        return make_response("Maintenance disabled", 200)

    msg = request.json
    meter = msg["Meter"]
    last_request = datetime.now()
    logging.info(f"SET meter from host {request.host} to {meter}")
    return make_response("Meter updated to " + str(meter), 200)


def restart():
    # Restart device
    return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)


def activate_maintenance():
    global maintenance_activation_time

    msg = request.json

    if msg["Active"] is None or not isinstance(msg["Active"], bool):
        return make_response("Invalid JSON body", 500)
    if msg["Active"]:
        maintenance_activation_time = datetime.now()
        logging.info(f"Activated maintenance from host {request.host}")
        return make_response("Maintenance activated", 200)
    else:
        maintenance_activation_time = datetime.fromisocalendar(1000, 1, 1)
        logging.info(f"Deactivated maintenance from host {request.host}")
        return make_response("Maintenance deactivated", 200)


def renew_cert():
    # Renew the company certificate
    return make_response("Certificate renewed", 200)


def update_meter(last_request, meter):
    cur_time = datetime.now()
    passed_sec = (cur_time - last_request).total_seconds()
    amount_added = random.uniform(average_kwh_per_sec - float("1e-5"), average_kwh_per_sec + float("1e-5"))
    meter += passed_sec * amount_added
    logging.info(f"Updated meter to {meter}")
    return meter


def factory_reset():
    # Triggers the factory reset
    logging.warning("Factory reset triggered")
    init()


def cut_off_power():
    # Cut off the power
    logging.warning("Power cut off triggered")

# init()
