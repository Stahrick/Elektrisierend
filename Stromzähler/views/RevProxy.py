# This a virtual reverse proxy to distribute requests to the wanted meter
import datetime
import json
import logging
import re
import threading

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from flask import Blueprint, make_response, request, redirect, url_for

from GlobalStorage import list_meters, get_meter, add_meter
from SmartMeter import Meter
from Config import cookie_sign_key
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

sessions_in_use = {}


@meter_management.route("/order/", methods=["POST"])
@clearance_level_required(ClearanceLevel.MEDIUM)
def meter_creation():
    data = request.json
    if "uuid" not in data:
        return "No uuid provided", 400
    uuid = data["uuid"]
    meter = Meter(uuid)
    add_meter(meter)
    return f"{meter.uuid}", 200


@revproxy.route("/setup/", methods=["POST"])
@clearance_level_required(ClearanceLevel.LOCAL)
@device_required
def meter_setup(device_uuid, device: Meter):
    data = request.json
    if not isinstance(data, dict) or "registrationCode" not in data:
        return "No registrationCode provided", 400

    try:
        with open("./sign_test_key.pub", "rb") as f:
            pub_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
        reg_code = jwt.decode(data["registrationCode"], pub_key, issuer="msb", audience=str(device_uuid), algorithms="RS512")
    except jwt.exceptions.InvalidTokenError:
        return "registrationCode invalid", 400
    return device.setup_meter(reg_code)


@revproxy.route("/activate-maintenance/", methods=["GET"])
@clearance_level_required(ClearanceLevel.LOW)
@device_required
def meter_maintenance_activation(device_uuid, device: Meter):
    # Check cookie based on pub signature
    try:
        with open("./sign_test_key.pub", "rb") as f:
            pub_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
        temp_code_enc = request.args.get("code", "no-code", str)
        temp_code = jwt.decode(temp_code_enc, pub_key, issuer="msb", audience="smartmeter", algorithms="RS512")
    except jwt.exceptions.InvalidTokenError:
        return "Invalid or no cookie provided"
    if not {"device_uuid", "user_id", "exp"}.issubset(temp_code.keys()):
        return "Missing information in code", 400
    if temp_code["device_uuid"] != str(device_uuid):
        return "Problem with provided device uuid", 400
    if (temp_code["user_id"], temp_code["device_uuid"]) in sessions_in_use:
        logging.error(f"Duplicate auth code redemption for {(temp_code["user_id"], temp_code["device_uuid"])}")
        return "Auth code was already redeemed", 400
    sessions_in_use[temp_code["user_id"], temp_code["device_uuid"]] = temp_code["exp"]

    # TODO check re url
    redirect_url = request.args.get('next') or request.referrer
    if not redirect_url or not re.compile("^https?://(localhost|127\\.0\\.0\\.1):5000/").match(redirect_url):
        redirect_url = url_for("service-worker.index")

    # Create meter cookie
    payload = {"iss": "smartmeter", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),
               "id": temp_code["user_id"], "device_uuid": temp_code["device_uuid"]}
    cookie = jwt.encode(payload, cookie_sign_key, algorithm="HS512")
    logging.info(f"Activated maintenance for {payload["id"]} on meter {device_uuid}")
    resp = make_response(redirect(redirect_url))
    resp.set_cookie("maintenance-" + str(device_uuid), cookie, secure=True, httponly=True, expires=payload["exp"],
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
    except ValueError:
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


def clean_sessions():
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    for elem in list(sessions_in_use.items()):
        if elem[1] < now:
            del sessions_in_use[elem[0]]
    threading.Timer(60, clean_sessions).start()


def send_meters():
    for meter_uuid in list_meters():
        get_meter(meter_uuid).send_meter()
    logging.info("Send all meter information")
    threading.Timer(1 * 60, send_meters).start()



