from flask import Blueprint, request, make_response

import requests

meter = Blueprint("metercommunication", __name__)

@meter.route("/register/", methods=["POST"])
def register_meter():
    data = request.json
    uuid = data["uuid"]
    code = data["code"]
    meter_cert = data["meter-cert"]

    # TODO Sign cert sign request and send signed back
    # TODO Send contract data
    return f"Registration complete with uuid ({uuid})", 200

@meter.route("/data/", methods=["POST"])
def get_meter_data():
    data = request.json
    uuid = data["uuid"]
    consumption_data = data["consumption"]

