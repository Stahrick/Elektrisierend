# Functions/View for the maintainer


from flask import Blueprint, render_template, request, make_response
import time

from GlobalStorage import add_meter, list_meters, get_meter
from SmartMeter import Meter

management = Blueprint("service-worker", __name__)

in_transit_mails = []


@management.route("/", methods=["GET"])
def index():
    return render_template("management.html", meter_list=list_meters())


@management.route("/list/", methods=["GET"])
def list():
    return list_meters()


@management.route("/create/", methods=["GET"])
def create_meter():
    meter = Meter()
    add_meter(meter)
    return f"Added meter with uuid {meter.uuid}", 200


@management.route("/setup/", methods=["POST"])
def setup_meter():
    data = request.json
    if "uuid" not in data or "registrationCode" not in data:
        return make_response("Invalid json", 401)
    devices = list_meters()
    device: Meter = get_meter(data["uuid"])
    if device is None:
        return make_response("Invalid uuid", 401)
    device.setup_meter(data["registrationCode"])
    return make_response(f"Device({device.uuid}) setup complete", 200)


@management.route("/receive_mails/", methods=["POST"])
def recv_mails():
    # Receive mails from Messstellenbetreiber
    global in_transit_mails
    data = request.json
    cur_time = time.time()
    if len(data) == 0:
        return make_response("No mails provided", 401)
    for mail in data:
        in_transit_mails.append([mail, cur_time])
    #in_transit_mails.extend(data)
    return make_response("Mails received", 200)


@management.route("/transfer-mails/", methods=["GET"])
def transfer_mails():
    global in_transit_mails
    new_mails = in_transit_mails
    in_transit_mails.clear()
    return new_mails
