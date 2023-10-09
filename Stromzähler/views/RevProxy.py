# This a virtual reverse proxy to distribute requests to the wanted meter

from flask import Flask, Blueprint, make_response, request

from GlobalStorage import list_meters, get_meter, add_meter
from SmartMeter import Meter
from security.Decorator import clearance_level_required, device_required, ClearanceLevel

import re

revproxy = Blueprint("revproxy", __name__)

clearances = {
    "local": {"setup": "setup_meter"},
    "company_portal": ["activate_maintenance"],
    "maintenance": ["restart", "cert_renew", "set_meter"]
}
local_ip_pattern = re.compile("^192\.168\.")


@revproxy.route("/order/", methods=["POST"])
@clearance_level_required(ClearanceLevel.MEDIUM)
def meter_creation():
    data = request.json
    if "uuid" not in data:
        return "No uuid provided", 400
    uuid = data["uuid"]
    meter = Meter(uuid)
    add_meter(meter)
    return f"Meter ordered with UUID ({meter.uuid})", 200

@revproxy.route("/<uuid:device_uuid>/setup", methods=["POST"])
@clearance_level_required(ClearanceLevel.LOCAL)
@device_required
def meter_setup(device_uuid, device: Meter):
    data = request.json
    if "registrationCode" not in data:
        return "No registrationCode provided", 400
    reg_code = data["registrationCode"]
    return device.setup_meter(reg_code)


# TODO Action verification with security levels and protection of attribute values
@revproxy.route("/<uuid:device_uuid>/<action>", methods=["GET", "POST"])
def trigger_meter_action(device_uuid, action):
    global clearances
    device_uuid = str(device_uuid)
    action = str(action)

    if action.startswith("__") or action.endswith("__"):
        return make_response("Action not found", 404)

    if action == "create":
        data = request.json
        if data is None or data["uuid"] is None:
            return make_response("Invalid json", 400)
        meter = Meter(data["uuid"])
        add_meter(meter)
        return make_response("Ordered ")

    device: Meter = get_meter(device_uuid)

    if action in clearances["local"]:
        global local_ip_pattern
        if not local_ip_pattern.match(request.host):
            return make_response("Not allowed", 401)
        if request.method == "GET":
            return getattr(device, action)()
        elif request.method == "POST":
            return getattr(device, action)(request)
    elif action in clearances["company_portal"]:
        # TODO Check if it is company connection
        if request.method == "GET":
            return getattr(device, action)()
        elif request.method == "POST":
            return getattr(device, action)(request)
    elif action in clearances["maintenance"]:
        # TODO Check for requester token
        if not device.is_in_maintenance():
            return make_response("Maintenance mode not enabled")
        if request.method == "GET":
            return getattr(device, action)()
        elif request.method == "POST":
            return getattr(device, action)(request)
    else:
        return make_response("Action not found", 404)

# @meter.route("/meter/", methods=["GET"])
# @app.route("/meter/<uuid:device_uuid>/", methods=["POST"])
# @app.route("/restart/", methods=["GET"])
# @app.route("/maintenance/", methods=["POST"])
# @app.route("/certrenew/", methods=["POST"])
