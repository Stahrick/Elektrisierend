from flask import Blueprint, request, make_response
from webportal_msb.api_requests import sign_cert

import requests

meter = Blueprint("metercommunication", __name__)

@meter.route("/register/", methods=["POST"])
def register_meter():
    data = request.json
    uuid = data["uuid"]
    code = data["code"]
    meter_csr = data["meter-cert"].encode('utf-8')
    meter_cert = sign_cert(meter_csr)
    # TODO Send contract data based on code
    return {"meter_cert": meter_cert}, 200

@meter.route("/data/", methods=["POST"])
def get_meter_data():
    data = request.json
    uuid = data["uuid"]
    consumption_data = data["consumption"]
    return "Received data", 200

