# This a virtual reverse proxy to distribute requests to the wanted meter
import json
import re
import threading
import time
import logging
import datetime
import jwt

import requests
from flask import Flask, Blueprint, make_response, request, redirect, url_for
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from GlobalStorage import list_meters, get_meter, add_meter
from SmartMeter import Meter
from security.Decorator import clearance_level_required, device_required, ClearanceLevel

logging.getLogger(__name__)

meter_management = Blueprint("metermanagement", __name__)
revproxy = Blueprint("revproxy", __name__)

meter_management.register_blueprint(revproxy, url_prefix="/<uuid:device_uuid>")

clearances = {
    "local": {"setup": "setup_meter"},
    "company_portal": ["activate_maintenance"],
    "maintenance": ["restart", "cert_renew", "set_meter"]
}


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
    if not isinstance(data, dict) or "registrationCode" not in data:
        return "No registrationCode provided", 400

    try:
        reg_code = json.loads(data["registrationCode"])
    except json.JSONDecodeError as e:
        return "registrationCode not parseable", 400
    return device.setup_meter(reg_code)


@revproxy.route("/activate-maintenance/", methods=["GET"])
@clearance_level_required(ClearanceLevel.LOW)
@device_required
def meter_maintenance_activation(device_uuid, device: Meter):
    # Check cookie based on pub signature
    try:
        with open("./sign_test_key.pub", "rb") as f:
            pub_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
        cookie_enc = request.args.get("cookie", "no-cookie", str)
        cookie = jwt.decode(cookie_enc, pub_key, issuer="msb", algorithms="RS512")
    except jwt.exceptions.InvalidTokenError as e:
        return "Invalid or no cookie provided"
    if not set(["device_uuid", "user_id", "exp"]).issubset(cookie.keys()):
        return "Missing information in cookie", 400
    if cookie["device_uuid"] != str(device_uuid):
        return "Problem with provided device uuid", 400
    # TODO check re url
    redirect_url = request.args.get('next') or request.referrer
    if not redirect_url or not re.compile("^https?://(localhost|127\\.0\\.0\\.1):5000/").match(redirect_url):
        redirect_url = url_for("service-worker.index")

    resp = make_response(redirect(redirect_url))
    #expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    expiration_time = cookie["exp"]
    resp.set_cookie("maintenance-"+str(device_uuid), cookie_enc, secure=True, httponly=True, expires=expiration_time,
                    max_age=datetime.timedelta(minutes=5))
    return resp


@revproxy.route("/set/", methods=["POST"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_set_consumption(device_uuid, device: Meter, user_id):
    data = request.json
    if "amount" not in data:
        return "No amount specified", 400
    try:
        amount = float(data["amount"])
    except ValueError as e:
        return "Amount not an int", 400
    return device.set_meter(amount)


@revproxy.route("/restart/", methods=["GET"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_restart(device_uuid, device: Meter, user_id):
    return device.restart()


@revproxy.route("/swap-certificate/", methods=["POST"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def meter_swap_certificate(device_uuid, device: Meter, user_id):
    # TODO Check certificate
    data = request.json
    if "cert" not in data:
        return "Certificate missing", 401
    new_cert = data["cert"]
    return device.swap_certificate(new_cert)

@revproxy.route("/push-update/", methods=["POST"])
@clearance_level_required(ClearanceLevel.HIGH)
@device_required
def push_update(device_uuid, device: Meter):
    return "Update pushed", 200

def send_meters():
    for meter_uuid in list_meters():
        get_meter(meter_uuid).send_meter()
    logging.info("Send all meter information")
    threading.Timer(1*60, send_meters).start()
