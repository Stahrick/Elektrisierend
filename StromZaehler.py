import os
import random
import math
import logging
import sys

from datetime import datetime
from flask import Flask, request, make_response

app = Flask(__name__)
logging.basicConfig("./log.txt", encoding="UTF-8", format='%(asctime)s %(levelname)s:%(message)s',filemode="w", level=logging.INFO)

meter = None
last_request = None
maintenance_activation_time = None

average_kwh_per_sec = 2050 / 365 / 24 / 60 / 60  # Average 2050kwh per person per year


@app.route("/meter", methods=["GET"])
def get_meter():
    update_meter()
    logging.info(f"GET meter from host {request.host}")
    return {"Meter": round(meter, 4)}


@app.route("/meter", methods=["POST"])
def set_meter():
    global maintenance_activation_time
    global last_request
    global meter

    cur_time = datetime.now()
    # Check if maintenance mode was activated more than 5 minutes ago
    if maintenance_activation_time is None or ((cur_time-maintenance_activation_time).total_seconds()/60) > 5:
        logging.warning(f"Try to SET meter from host {request.host}, but failed caused by deactivated maintenance mode")
        return make_response("Maintenance disabled", 200)

    msg = request.json
    meter = msg["Meter"]
    last_request = datetime.now()
    logging.info(f"SET meter from host {request.host} to {meter}")
    return make_response("Meter updated to " + str(meter), 200)


@app.route("/restart", methods=["GET"])
def restart():
    # Restart device
    return make_response("Restart triggered. Wait at least 30 sec before reconnecting.", 200)


@app.route("/maintenance", methods=["POST"])
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
        maintenance_activation_time = datetime.fromisocalendar(1000,1,1)
        logging.info(f"Deactivated maintenance from host {request.host}")
        return make_response("Maintenance deactivated", 200)


#@app.route("/certrenew", methods=["POST"]):
def renew_cert():
    # Renew the company certificate
    return make_response("Certificate renewed", 200)

def update_meter():
    global meter
    cur_time = datetime.now()
    passed_sec = (cur_time-last_request).total_seconds()
    amount_added = random.uniform(average_kwh_per_sec-float("1e-5"), average_kwh_per_sec+float("1e-5"))
    meter += passed_sec * amount_added
    logging.info(f"Updated meter to {meter}")


def start_server():
    logging.info("Start webserver")
    app.run(host="0.0.0.0", debug=True, port=80)


def init():
    global meter
    global last_request
    meter = random.randrange(0, 50)
    last_request = datetime.now()
    logging.info(f"Initialized meter with {meter} KWH and last_request {last_request}")


def factory_reset():
    # Triggers the factory reset
    logging.warning("Factory reset triggered")
    init()

init()
start_server()

