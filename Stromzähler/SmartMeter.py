import random
import logging
import threading

import requests

from datetime import datetime

from cryptography import x509
from flask import make_response
from uuid import uuid4

from security.Certificate import create_X509_csr
from GlobalStorage import remove_meter, add_meter

logging.getLogger(__name__)

average_kwh_per_sec = 2050 / 365 / 24 / 60 / 60  # Average 2050kwh per person per year


class Meter:
    uuid = None
    meter = None
    last_update = None
    configuration = {"maintainer_cert": None, "maintainer_url": None, "own_cert": None}

    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid

    def check_setup_complete(f):
        def decorator(self, *args, **kwargs):
            if None in self.configuration.values():
                return "Meter not setup", 400
            return f(self, *args, **kwargs)

        return decorator

    def setup_meter(self, registration_config):
        # Check uuid in registration_code with device uuid
        if self.uuid != registration_config["uuid"]:
            logging.info(f"Invalid registration config provided for device({self.uuid}): {registration_config}")
            return make_response("Invalid registration code provided", 400)
        code = registration_config["code"]
        self.configuration["own_cert"] = create_X509_csr(self.uuid)
        self.configuration["maintainer_cert"] = "Hier könnte ihr Cert stehen"
        req_data = {"uuid": self.uuid, "code": code, "meter-cert": self.configuration["own_cert"]}
        try:
            r = requests.post(f"{registration_config["url"]}/register/", json=req_data)
            if r.status_code != 200:
                self.configuration["own_cert"] = None
                return make_response("Meter registration failed", 406)
            res = r.json()
            if "meter_cert" not in res:
                self.configuration["own_cert"] = None
                return make_response("Meter registration failed", 406)
            self.configuration["own_cert"] = x509.load_pem_x509_certificate(res["meter_cert"].encode('utf-8'))
        except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError) as e:
            return make_response("Meter registration failed", 406)
        self.meter = random.randrange(0, 50)
        self.last_update = datetime.now()
        self.configuration["maintainer_url"] = registration_config["url"]
        logging.info(f"Initialized meter with {self.meter} KWH")
        return make_response("Meter setup complete", 200)

    @check_setup_complete
    def set_meter(self, amount):
        self.meter = amount
        logging.info(f"SET meter to {self.meter}")
        return make_response(f"Set consumption to {self.meter}", 200)

    #@check_setup_complete
    def restart(self):
        # Restart device
        def add_again(): add_meter(self)
        remove_meter(self.uuid)
        threading.Timer(30, add_again).start()
        logging.warning("Restart triggered")
        return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)

    @check_setup_complete
    def swap_certificate(self, new_cert):
        # Swap the maintainer certificate
        logging.warning("Certificate swap triggered")
        self.configuration["maintainer_cert"] = new_cert
        return make_response("Certificate renewed", 200)

    @check_setup_complete
    def send_meter(self):
        global average_kwh_per_sec
        # if self.configuration["maintainer_url"] is None:
        #    return
        cur_time = datetime.now()
        passed_sec = (cur_time - self.last_update).total_seconds()
        amount_added = random.uniform(average_kwh_per_sec - float("1e-5"), average_kwh_per_sec + float("1e-5"))
        self.meter += passed_sec * amount_added
        # TODO add verify= to check server cert
        requests.post(f"{self.configuration["maintainer_url"]}/data/",
                      json={"uuid": self.uuid, "consumption": self.meter}, cert=self.configuration["own_cert"])
        logging.info(f"SEND meter data {self.meter} Kwh")

    @check_setup_complete
    def factory_reset(self):
        # Triggers the factory reset
        logging.warning("Factory reset triggered")
        self.__init__()

    @check_setup_complete
    def cut_off_power(self):
        # Cut off the power
        from GlobalStorage import remove_meter
        logging.warning("Power cut off triggered")
        remove_meter(self.uuid)
