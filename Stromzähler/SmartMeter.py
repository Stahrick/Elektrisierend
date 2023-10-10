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
    configuration = {"maintainer_cert": None, "maintainer_url": None, "own_cert": None}

    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid

    def setup_meter(self, registration_code):
        # TODO Check signature and hash verification
        # Check uuid in registration_code with device uuid
        if self.uuid != registration_code["uuid"]:
            logging.info(f"Invalid registration code provided for device({self.uuid}): {registration_code}")
            return make_response("Invalid registration code provided", 400)
        # TODO Generate own certificate

        self.meter = random.randrange(0, 50)
        logging.info(f"Initialized meter with {self.meter} KWH")
        return make_response("Meter setup complete", 200)

    def activate_maintenance(self):
        self.maintenance_activation_time = datetime.now()
        logging.info(f"Activated maintenance from host {req.host}")

    def set_meter(self, amount):
        self.meter = amount
        logging.info(f"SET meter to {self.meter}")

    def restart(self):
        # Restart device
        logging.warning("Restart triggered")
        return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)

    def swap_certificate(self, new_cert):
        # Swap the maintainer certificate
        logging.warning("Certificate swap triggered")
        self.configuration["cert"] = new_cert
        return make_response("Certificate renewed", 200)

    def send_meter(self):
        global average_kwh_per_sec
        cur_time = datetime.now()
        passed_sec = (cur_time - self.last_update).total_seconds()
        amount_added = random.uniform(average_kwh_per_sec - float("1e-5"), average_kwh_per_sec + float("1e-5"))
        self.meter += passed_sec * amount_added
        # TODO Add url
        requests.post(self.configuration["url"], {"uuid": self.uuid, "meter": self.meter})
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

