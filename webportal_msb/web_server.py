import datetime
import logging

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from flask import Flask, render_template, request, redirect, url_for, make_response, session
from os import urandom
from urllib.parse import urljoin, quote

from views.metercommunication import meter
from views.electricityprovider import provider

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True

app.register_blueprint(meter, url_prefix="/meter")
app.register_blueprint(provider, url_prefix="/provider")


# todo: login, register, logout logic; fingerprint, css, database, password requirements
# support, "email confirm"
#

def check_session(uuid):
    # checks if uuid exists and is valid returns account data
    if uuid is None:
        return False
    if "uuid" in uuid:
        print(uuid)
        # hier muss noch die datenbank zuordnung kommen, und check ob es die uuid gibt
        return {"uuid": 123, "username": "testo", "first_name": "Shadow", "last_name": "Sama", "email": "cum@me.com",
                "iban": "DE123654", "phone": "+49112", "city": "Madenheim", "zip_code": "69069",
                "address": "Wallstreet", "house": "3", "em_id": "DEADBEEF4269", "em_reading": 911.69,
                "contract_id": "{{ 7*7 }}"}

    return False


def check_login(username, password):
    return {'uuid': 'uuid', 'role': 'technician'}


def check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
    return True


def update_user_data(username, email, phone, iban):
    return True


def get_contract_data(contract_id):
    return {"uuid": 123, "username": "testo", "first_name": "Shadow", "last_name": "Sama", "email": "cum@me.com",
            "iban": "DE123654", "phone": "+49112", "state": "Germany", "city": "Madenheim", "zip_code": "69069",
            "address": "Wallstreet 3", "em_id": "DEADBEEF4269", "em_reading": 911.69, "contract_id": "\{\{ 7*7 \}\}"}


def get_ems_by_contract():
    try:
        r = requests.get("http://localhost:25565/service-worker/list/", timeout=5)
        meter_uuids = r.json()
    except Exception as e:
        meter_uuids = [urandom(6).hex() for _ in range(6)]
    return [[uuid for uuid in meter_uuids], [urandom(6).hex() for _ in range(len(meter_uuids))],
            [i for i in range(len(meter_uuids))]]


def check_em_id(em):
    return True


def activate_maintenance(id):
    return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        valid = check_login(username, password)
        if valid:
            response = make_response(redirect(url_for('home')))
            session['uuid'] = valid['uuid']
            session['role'] = valid['role']
            return response
        else:
            session.clear()
            return render_template('login.html', error='invalid login')
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    session.clear()
    return response


@app.route('/home', methods=['GET', 'POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if session.get('role') == 'office':
            if request.args.get('msg') == 'ici':
                error = 'your contract ID is invalid'
                return render_template('office.html', msg=error)
            return render_template('office.html')
        elif session.get('role') == 'technician':
            msg = request.args.get('msg')
            if msg is not None:
                if msg == 'invalid':
                    msg = 'The selected Elecricity Meter could\'nt be set to maintenance mode'
                if msg == 'active':
                    msg = 'Elecricity Meter: ' + request.args.get('id') + ' has been set to maintenance mode'
            em_contracts = get_ems_by_contract()
            return render_template('technician.html', em_ids=em_contracts, entries=len(em_contracts[0]), msg=msg)
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/show_contract', methods=['POST'])
def show_contract():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if 'contract_id' in request.form:
            contract_id = request.form['contract_id']
            contract_data = get_contract_data(contract_id)
            if contract_data:
                return render_template('show_contract.html', contract_id=contract_data['contract_id'],
                                       em_id=contract_data['em_id'], em_reading=contract_data['em_reading'],
                                       state=contract_data['state'], zip_code=contract_data['zip_code'],
                                       city=contract_data['city'], address=contract_data['address'],
                                       iban=contract_data['iban'], phone=contract_data['phone'],
                                       email=contract_data['email'], username=contract_data['username'],
                                       first_name=contract_data['first_name'], last_name=contract_data['last_name'])
            else:
                # das lässt gerade template injections zu
                return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/edit_contract', methods=['GET', 'POST'])
def edit_contract():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # checks if post request with correct data value pairs
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            iban = request.form['iban']
            if update_user_data(username, email, phone, iban):
                # trys to update database and redirects to profile if it did
                # updates values for account that owns the cookie
                return redirect(url_for('profile'))
            else:
                # returns error if it cant update
                return render_template('edit_profile', username=username, email=email, phone=phone, iban=iban,
                                       error='Cant update your Profile')
        if request.args.get('contract_id') is not None:
            contract_data = get_contract_data(request.args.get('contract_id'))
            if contract_data:
                return render_template('edit_contract.html', contract_id=contract_data['contract_id'],
                                       em_id=contract_data['em_id'], em_reading=contract_data['em_reading'],
                                       state=contract_data['state'], zip_code=contract_data['zip_code'],
                                       city=contract_data['city'], address=contract_data['address'],
                                       iban=contract_data['iban'], phone=contract_data['phone'],
                                       email=contract_data['email'], username=contract_data['username'],
                                       first_name=contract_data['first_name'], last_name=contract_data['last_name'])
        return redirect(url_for('home') + '?msg=ici')
    return redirect(url_for('login'))


@app.route('/maintenance', methods=['GET'])
def maintenance():
    user_data = check_session(session.get('uuid'))
    if user_data:
        id = request.args.get('id')
        if session.get('role') == 'technician' and id is not None:
            if check_em_id(id):
                case_id = request.args.get("case-id", "")
                # TODO check case_id exist in DB and is connected to device uuid
                if case_id == "":
                    return redirect(url_for('home') + '?msg=invalid')
                valid_referrer = urljoin(urljoin(request.url_root, url_for("handle_support_case")), f"?case-id={case_id}")
                if request.referrer != valid_referrer:
                    # Ensure user requests from support ticket or seriously manipulate request
                    return redirect(url_for('home') + '?msg=invalid')
                if activate_maintenance(id):
                    with open("./sign_test_key.pem", "rb") as f:
                        priv_key = serialization.load_pem_private_key(
                            f.read(), password=None, backend=default_backend()
                        )
                    cookie_data = {"iss": "msb", "aud": "smartmeter", "device_uuid": str(id),
                                   "user_id": user_data["uuid"],
                                   "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=20)}
                    encoded = jwt.encode(cookie_data, priv_key, algorithm="RS512")
                    red_url_enc = quote(urljoin(request.url_root, url_for("home")), safe="")
                    logging.info(f"User [{cookie_data["user_id"]}] activated maintenance for "
                                 f"device [{cookie_data["device_uuid"]}] connected to support case [{case_id}]")
                    return redirect(
                        f"http://localhost:25565/meter/{id}/activate-maintenance/?code={encoded}&next={red_url_enc}")
    else:
        return redirect(url_for('home') + '?msg=invalid')


@app.route("/support-case/", methods=["GET", "POST"])
def handle_support_case():
    case_id = request.args.get("case-id", "")
    if case_id == "":
        return render_template("technician.html", case_data=None)

    # TODO get case data from DB
    case_data = {
        "case_id": 117343424,
        "title": "Example title",
        "opened": datetime.datetime.now(),
        "status": "Open",
        "device_uuid": "5f27812d-a9b4-4945-a195-8b0d2b889967",
        "description": "Consumption goes up too fast. User complains about high usage and resulting fees",
        "opened_by": "Deez Nutz",
        "comments": [{"name": "Popi Aram", "comment": "Maybe has to be restarted.", "time": datetime.datetime.now()}, {"name": "Will Fit", "comment": "Transfer ticket over to technician", "time": datetime.datetime.now()}]
    }
    return render_template("technician.html", case_data=case_data)


app.run(debug=True, port=5000)
