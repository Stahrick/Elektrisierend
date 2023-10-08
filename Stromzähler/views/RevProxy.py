# This a virtual reverse proxy to distribute requests to the wanted meter
from flask import Flask, Blueprint, make_response

from Stromzähler.SmartMeter import web_access_functions
from Stromzähler.GlobalStorage import list_meters, get_meter

revproxy = Blueprint("revproxy", __name__)

# TODO Action verification with security levels and protection of attribute values
@revproxy.route("/<uuid:device_uuid>/<action>", methods=["GET"])
def trigger_meter_action(device_uuid, action):
    device_uuid = str(device_uuid)
    if device_uuid not in list_meters():
        return make_response("UUID not found", 404)
    if action not in web_access_functions:
        return make_response("Action not found", 404)

    device = get_meter(device_uuid)
    return getattr(device, action)()
    # return make_response(func_ret["text"], func_ret["status"])

# @meter.route("/meter/", methods=["GET"])
# @app.route("/meter/<uuid:device_uuid>/", methods=["POST"])
# @app.route("/restart/", methods=["GET"])
# @app.route("/maintenance/", methods=["POST"])
# @app.route("/certrenew/", methods=["POST"])
