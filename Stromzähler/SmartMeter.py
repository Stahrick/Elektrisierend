import random
import logging
import requests

from datetime import datetime
from flask import make_response
from uuid import uuid4

from Config import msb_url
from security.Certificate import create_X509_csr

logging.getLogger(__name__)

average_kwh_per_sec = 2050 / 365 / 24 / 60 / 60  # Average 2050kwh per person per year


class Meter:
    uuid = None
    meter = None
    last_update = None
    maintenance_activation_time = None
    configuration = {"maintainer_cert": None, "maintainer_url": None, "own_cert": None}

    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid

    def setup_meter(self, registration_config):
        # TODO Check signature and hash verification
        # Check uuid in registration_code with device uuid
        if self.uuid != registration_config["uuid"]:
            logging.info(f"Invalid registration config provided for device({self.uuid}): {registration_config}")
            return make_response("Invalid registration code provided", 400)
        code = registration_config["code"]
        self.configuration["own_cert"] = create_X509_csr(self.uuid)
        req_data = {"uuid": self.uuid, "code": code, "meter-cert": self.configuration["own_cert"]}
        try:
            r = requests.post(f"{registration_config["url"]}/register/", json=req_data)
            if r.status_code != 200:
                return make_response("Meter registration failed", 406)
        except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError) as e:
            return make_response("Meter registration failed", 406)
        self.meter = random.randrange(0, 50)
        self.last_update = datetime.now()
        self.configuration["maintainer_url"] = registration_config["url"]
        logging.info(f"Initialized meter with {self.meter} KWH")
        return make_response("Meter setup complete", 200)

    def activate_maintenance(self):
        self.maintenance_activation_time = datetime.now()
        logging.info(f"Activated maintenance mode")

    def set_meter(self, amount):
        self.meter = amount
        logging.info(f"SET meter to {self.meter}")
        return make_response(f"Set consumption to {self.meter}", 200)

    def restart(self):
        # Restart device
        logging.warning("Restart triggered")
        return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)

    def swap_certificate(self, new_cert):
        # Swap the maintainer certificate
        logging.warning("Certificate swap triggered")
        self.configuration["maintainer_cert"] = new_cert
        return make_response("Certificate renewed", 200)

    def send_meter(self):
        global average_kwh_per_sec
        if self.configuration["maintainer_url"] is None:
            return
        cur_time = datetime.now()
        passed_sec = (cur_time - self.last_update).total_seconds()
        amount_added = random.uniform(average_kwh_per_sec - float("1e-5"), average_kwh_per_sec + float("1e-5"))
        self.meter += passed_sec * amount_added
        requests.post(f"{self.configuration["maintainer_url"]}/data/", json={"uuid": self.uuid, "consumption": self.meter})
        logging.info(f"SEND meter data {self.meter} Kwh")

    def is_in_maintenance(self):
        cur_time = datetime.now()
        return (self.maintenance_activation_time is not None
                and ((cur_time - self.maintenance_activation_time).total_seconds() / 60) < 5)

    def factory_reset(self):
        # Triggers the factory reset
        logging.warning("Factory reset triggered")
        self.__init__()

    def cut_off_power(self):
        # Cut off the power
        from GlobalStorage import remove_meter
        logging.warning("Power cut off triggered")
        remove_meter(self.uuid)

