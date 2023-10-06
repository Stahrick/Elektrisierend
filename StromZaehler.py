import random
import math

from datetime import datetime
from flask import Flask, request, make_response

app = Flask(__name__)

meter = 0
last_request = 0
maintenance_activation_time = datetime.fromisocalendar(1000,1,1)

average_kwh_per_sec = 2050 / 365 / 24 / 60 / 60  # Average 2050kwh per person per year


@app.route("/meter", methods=["GET"])
def get_meter():
    update_meter()
    return {"Meter": round(meter, 4)}


@app.route("/meter", methods=["POST"])
def set_meter():
    global maintenance_activation_time
    global last_request
    global meter

    cur_time = datetime.now()
    if ((cur_time-maintenance_activation_time).total_seconds()/60) > 5:
        return make_response("Maintenance disabled", 200)

    msg = request.json
    meter = msg["Meter"]
    last_request = datetime.now()
    return make_response("Meter updated to " + str(meter), 200)


@app.route("/maintenance", methods=["POST"])
def activate_maintenance():
    global maintenance_activation_time

    msg = request.json

    if msg["Active"] is None or not isinstance(msg["Active"], bool):
        return make_response("Invalid JSON body", 500)
    if msg["Active"]:
        maintenance_activation_time = datetime.now()
        return make_response("Maintenance activated", 200)
    else:
        maintenance_activation_time = datetime.fromisocalendar(1000,1,1)
        return make_response("Maintenance deactivated", 200)


def update_meter():
    global meter
    cur_time = datetime.now()
    passed_sec = (cur_time-last_request).total_seconds()
    amount_added = random.uniform(average_kwh_per_sec-float("1e-5"), average_kwh_per_sec+float("1e-5"))
    meter += passed_sec * amount_added


def start_server():
    app.run(host="0.0.0.0", debug=True, port=80)


def init():
    global meter
    global last_request
    meter = random.randrange(0, 50)
    last_request = datetime.now()


init()
start_server()

