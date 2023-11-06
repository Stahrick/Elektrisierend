import random
import logging
import threading
from json import JSONEncoder
from pathlib import Path

import requests

from datetime import datetime

from cryptography import x509
from cryptography.hazmat.primitives import serialization
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
    configuration = None

    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.configuration = {"maintainer_cert": None, "maintainer_url": None, "own_cert": None, "priv_key": None}

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
        privkey_path, csr = create_X509_csr(self.uuid)
        req_data = {"uuid": self.uuid, "code": code, "meter-cert": csr}
        try:
            r = requests.post(f"{registration_config["url"]}/register/", json=req_data)
            if r.status_code != 200:
                self.configuration["own_cert"] = None
                return make_response("Meter registration failed", 406)
            res = r.json()
            if "meter_cert" not in res:
                self.configuration["own_cert"] = None
                return make_response("Meter registration failed", 406)

            cert_path = str(Path(__file__).parent / f"MeterCerts/{self.uuid}.pem")
            with open(cert_path, "w") as f:
                f.write(res["meter_cert"])
            self.configuration["own_cert"] = cert_path
            self.configuration["priv_key"] = privkey_path
        except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError) as e:
            return make_response("Meter registration failed", 406)
        self.meter = random.randrange(0, 50)
        self.last_update = datetime.now()
        self.configuration["maintainer_cert"] = "Hier könnte ihr Cert stehen"
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
        # TODO requests only allows to load cert, key itself -> You have to provide path
        requests.post(f"{self.configuration["maintainer_url"]}/data/",
                      json={"uuid": self.uuid, "consumption": self.meter},
                      cert=(self.configuration["own_cert"], self.configuration["priv_key"]))
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

    def to_dict(self):
        data = {
            "uuid": self.uuid,
            "meter": self.meter,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "configuration": self.configuration,
        }
        #if self.configuration["own_cert"]:
        #    data["configuration"]["own_cert"] = self.configuration["own_cert"].public_bytes(serialization.Encoding.PEM).decode('utf-8')
        #if self.configuration["maintainer_cert"]:
        #    data["configuration"]["maintainer_cert"] = self.configuration["maintainer_cert"].public_bytes(serialization.Encoding.PEM).decode('utf-8')
        return data

    @classmethod
    def from_dict(cls, data):
        meter = cls(data["uuid"])
        meter.meter = data["meter"]
        meter.last_update = datetime.fromisoformat(data["last_update"]) if data["last_update"] else None
        meter.configuration = data["configuration"]
        # if "own_cert" in data["configuration"]:
        #     meter.configuration["own_cert"] = x509.load_pem_x509_certificate(data["configuration"]["own_cert"].encode('utf-8'))
        # if "maintainer_cert" in data["configuration"]:
        #    meter.configuration["maintainer_cert"] = x509.load_pem_x509_certificate(data["configuration"]["maintainer_cert"].encode('utf-8'))
        return meter

class MeterEncoder(JSONEncoder):
    def default(self, o):
        #return {"uuid": o.uuid, "meter": o.meter,
        #        "last_update": o.last_update, "configuration": o.configuration}
        return o.__dict__

