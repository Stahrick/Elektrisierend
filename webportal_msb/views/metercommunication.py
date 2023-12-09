from flask import Blueprint, request, make_response
from api_requests import sign_cert
from database.EMDB import EmHandler
import requests
from dotenv import load_dotenv
from os import getenv
from config import kp_url

load_dotenv()
pw = getenv('MSBPW')
username = getenv('MSBUser')
dbname = getenv('MSBDB')

db_elmo_handler = EmHandler(username,pw,dbname)
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
    # TODO in die Verbrauchsdatenbank rein 
    data = request.json
    if request.method == 'POST' and 'uuid' in data and 'consumption' in data:
        em = db_elmo_handler.get_Em_by_id(data['uuid'])
        if em:
            em.em_consumption = data['consumption']
            success = db_elmo_handler.update_Em_by_id(data['uuid'],{"em_consumption": data['consumption']})
            if success:
                response = requests.post(f"{kp_url}/data/",json={"em": em})
                if response.status_code == 200:
                    make_response("success",200)
                else:
                    make_response("internal server error", 500)
        return make_response()
    return "Received data", 200

