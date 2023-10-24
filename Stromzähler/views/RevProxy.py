# This a virtual reverse proxy to distribute requests to the wanted meter
import json

import requests
from flask import Flask, Blueprint, make_response, request

from GlobalStorage import list_meters, get_meter, add_meter
from SmartMeter import Meter
from security.Decorator import clearance_level_required, device_required, ClearanceLevel

import re

meter_management = Blueprint("metermanagement", __name__)
revproxy = Blueprint("revproxy", __name__)

meter_management.register_blueprint(revproxy, url_prefix="/<uuid:device_uuid>")

clearances = {
    "local": {"setup": "setup_meter"},
    "company_portal": ["activate_maintenance"],
    "maintenance": ["restart", "cert_renew", "set_meter"]
}
local_ip_pattern = re.compile("^192\\.168\\.")


@meter_management.route("/order/", methods=["POST"])
@clearance_level_required(ClearanceLevel.MEDIUM)
def meter_creation():
    data = request.json
    if "uuid" not in data:
        return "No uuid provided", 400
    uuid = data["uuid"]
    meter = Meter(uuid)
    add_meter(meter)
    return f"Meter ordered with UUID ({meter.uuid})", 200

@revproxy.route("/setup/", methods=["POST"])
@clearance_level_required(ClearanceLevel.LOCAL)
@device_required
def meter_setup(device_uuid, device: Meter):
    data = request.json
    if "registrationCode" not in data:
        return "No registrationCode provided", 400

    # TODO Check if json can parse it
    reg_code = json.loads(data["registrationCode"])
    return device.setup_meter(reg_code)


@revproxy.route("/activate-maintenance/", methods=["GET"])
@clearance_level_required(ClearanceLevel.MEDIUM)
@device_required
def meter_maintenance_activation(device_uuid, device: Meter):
    device.activate_maintenance()
    resp = make_response("Maintenance activated for you for next 5 minutes", 200)
    # TODO Cookies
    resp.set_cookie("maintenance-"+device_uuid, 123)
    return "Maintenance activated for 5 minutes", 200


@revproxy.route("/set/", methods=["POST"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_set_consumption(device_uuid, device: Meter):
    data = request.json
    if "amount" not in data:
        return "No amount specified", 400
    amount = data["amount"]
    if not isinstance(amount, int):
        return "Amount not an int", 400
    # TODO Check for maintenance mode
    return device.set_meter(amount)


@revproxy.route("/restart/", methods=["GET"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_restart(device_uuid, device: Meter):
    return device.restart()


@revproxy.route("/swap-certificate", methods=["POST"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_swap_certificate(device_uuid, device: Meter):
    # TODO Check certificate
    data = request.json
    if "cert" not in data:
        return "Certificate missing", 401
    new_cert = data["cert"]
    return device.swap_certificate(new_cert)
