import datetime
import logging
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from uuid import uuid4
import requests
from config import kp_url, meter_url, mycert, root_ca
from passlib.hash import argon2
from api_requests import send_registration_mail
import json as JSON

import ssl
import werkzeug.serving
import OpenSSL

from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask_wtf.csrf import CSRFProtect
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.ContractDB import ContractHandler
from database.EMDB import EmHandler
from database.HistDataDB import HistDataHandler
from database.InternalDataclasses import Account, Contract, Em, HistData
from dotenv import load_dotenv
from urllib.parse import urljoin, quote

from views.metercommunication import meter
from views.electricityprovider import provider

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True
csrf = CSRFProtect(app)

load_dotenv()
pw = getenv('MSBPW')
username = getenv('MSBUser')
dbname = getenv('MSBDB')
db_acc_handler = AccountHandler(username, pw, dbname)
db_ctr_handler = ContractHandler(username, pw, dbname)
db_elmo_handler = EmHandler(username, pw, dbname)
db_hdt_handler = HistDataHandler(username, pw, dbname)

app.register_blueprint(meter, url_prefix="/meter")
app.register_blueprint(provider, url_prefix="/provider")


# todo: login, register, logout logic; fingerprint, css, database, password requirements
# support, "email confirm"
#

class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
    """
    We subclass this class so that we can gain access to the connection
    property. self.connection is the underlying client socket. When a TLS
    connection is established, the underlying socket is an instance of
    SSLSocket, which in turn exposes the getpeercert() method.
    The output from that method is what we want to make available elsewhere
    in the application.
    """
    def make_environ(self):
        """
        The superclass method develops the environ hash that eventually
        forms part of the Flask request object.
        We allow the superclass method to run first, then we insert the
        peer certificate into the hash. That exposes it to us later in
        the request variable that Flask provides
        """
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        print(x509_binary) 
        if x509_binary:
            x509 = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
            environ['peercert'] = x509
            return environ
        environ['peercert'] = None
        return environ


def check_session(uuid):
    # checks if uuid exists and is valid returns account data
    if uuid is None:
        return False
    acc = db_acc_handler.get_account_by_id(uuid)
    if acc:
        return acc
    return False


def check_login(username, password):
    res = db_acc_handler.get_account_by_username(username)
    if res and res[0]:
        res = res[0]
        try:
            if argon2.verify(password,res['pw_hash']):        
                return {'uuid': res['_id'], 'role': res['role']}
        except:
            return None
    return None

def check_register(data):
    return True  # no registration for msb, done by hand by db admin :D (currently)


# updates account data by given fields, ignores params all if data is given directly
# TODO please test
def update_user_data(acc_id, ctr_id = None,
                     username=None, pw=None,
                     first_name=None, last_name=None,
                     email=None, phone=None,
                     acc_state=None,
                     acc_city=None, acc_zip_code=None,
                     acc_address=None, acc_contract_id=None,
                     acc_data: dict = None,
                     iban=None, em_id=None,
                     ctr_state=None, ctr_city=None,
                     ctr_zip_code=None, ctr_address=None,
                     ctr_data: dict = None,
                     ) -> bool:
    if not ctr_id:
        acc = db_acc_handler.get_account_by_id(acc_id)
        if acc:
            ctr_id = acc['contract_id']
    if pw:
        pw = argon2.hash(pw)  # should only be accessible if already authenticated so np
    if  (username or pw or first_name or last_name or email or phone or acc_state or acc_city or acc_zip_code or acc_address or acc_contract_id or acc_data) and acc_id:
        b1 = _update_acc_data(acc_id, username= username, pw = pw, first_name = first_name, last_name = last_name, email = email, phone = phone, state= acc_state, city = acc_city, zip_code = acc_zip_code, address = acc_address, contract_id = acc_contract_id , data = acc_data)
    else:
        b1 = True
    if (iban or em_id or ctr_state or ctr_city or ctr_zip_code or ctr_address or ctr_data) and ctr_id :
        b2 = _update_contract_data(ctr_id, iban = iban, em_id = em_id, state = ctr_state, city = ctr_city, zip_code = ctr_zip_code, address = ctr_address, data = ctr_data)
    else:
        b2 = True
    if b1 and b2:
        return True
    return False

def _update_acc_data(_id, username=None, pw=None, first_name=None, last_name=None, email=None, phone=None, state=None,
                    city=None, zip_code=None, address=None, contract_id=None, data: dict = None) -> bool:
    params = locals()
    param = {k: v for k, v in params.items() if v}
    if param:
        del (param['_id'])
        if db_acc_handler.get_account_by_username(username):
            return False
        if 'data' in param:
            return db_acc_handler.update_account_by_id(_id, data)
        else:
            return db_acc_handler.update_account_by_id(_id, param)
    return False

def _update_contract_data(_id, date=None, iban=None, em_id=None, state=None, city=None, zip_code=None, address=None,
                         data: dict = None):
    params = locals()
    param = {k: v for k, v in params.items() if v is not None}
    if param:
        del (param['_id'])
        if 'data' in param:
            return db_ctr_handler.update_contract_by_id(_id, data)
        elif param:
            return db_ctr_handler.update_contract_by_id(_id, param)
    return True

def get_contract_data(contract_id):
    res = db_ctr_handler.get_contract_by_id(contract_id)
    print(res)
    return res


def get_ems_by_contract():
    dbres = db_ctr_handler.get_all()
    print(dbres)
    l1, l2, l = list(), list(), list()
    for i, r in enumerate(dbres):
        print(r)
        l1.append(r['em_id'])
        l2.append(r['_id'])
    return [l1, l2]


def check_em_id(id):
    res = db_elmo_handler.get_Em_by_id(id)
    if res:
        return True
    return False

def create_contract(_id : str, date : str, iban : str, state : str, city : str, zip_code : int, address : str, em_id : str):
    c = Contract(date = date,iban = iban, em_id = em_id,state=state,city=city,zip_code=zip_code,address = address, _id = _id)
    ctr = db_ctr_handler.create_contract(c)
    return ctr

def create_em(em : Em):
    e = db_elmo_handler.create_Em(em)
    h = db_hdt_handler.create_HistData(HistData([],_id = em.hist_id))
    if e and h:
        return e

@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    session.clear()
    return response


@app.route('/home/', methods=['GET', 'POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if session.get('role') == 'office':
            if request.args.get('msg') == 'ici':
                error = 'your contract ID is invalid'
                return render_template('office.html', msg=error)
            return render_template('office.html')
        elif session.get('role') == 'technician':
            em_contracts = get_ems_by_contract()
            return render_template('technician.html')
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/edit_contract/', methods=['GET', 'POST'])
def edit_contract():
    user_data = check_session(session.get('uuid'))
    if user_data and session.get('role')=='office':
        if request.method == 'POST' and request.form and 'contract_id' in request.form:
            print(request.form.to_dict())
            d = request.form.to_dict()
            print(d)
            data = dict()
            for k,v in d.items():
                if v and v !='':
                    data.update({k:v})
            data.pop('otp')
            print(data)
            """data['contract_id'] = d['contract_id']
            data['first_name'] = d['first_name']
            data['last_name'] = d['last_name']
            data['email'] = d['email']
            data['tel'] = d['tel']
            data['iban'] = d['iban']
            data['state'] = d['state']
            data['city'] = d['city']
            data['zip'] = d['zip']
            data['address'] = d['address']
            cid_kun = request.form.get('contract_id') 
            first_name = request.form.get('first_name') if request.form.get('first_name') else None
            last_name = request.form.get('last_name') if request.form.get('last_name') else None
            email = request.form.get('email') if request.form.get('email') else None
            tel = request.form.get('tel') if request.form.get('tel') else None
            iban = request.form.get('iban') if request.form.get('iban') else None
            state = request.form.get('state') if request.form.get('state') else None
            city = request.form.get('city') if request.form.get('city') else None
            zip_code = request.form.get('zip') if request.form.get('zip') else None
            address = request.form.get('address') if request.form.get('address') else None"""
            #contract_data = get_contract_data(request.args.get('contract_id'))
            response = requests.post(kp_url + "/data/user/", json=data,cert = mycert, verify=root_ca)
            if not response.status_code == 200:
                return render_template('edit_contract.html', user = request.form, contract=request.form,
                                       error='Cant update your Profile')
            output = JSON.loads(response.text) #returns user if successful
            ctr_id =  data['contract_id']
            first_name = data['first_name'] if'first_name' in data else None
            last_name = data['last_name'] if 'last_name' in data else None
            email = data['email'] if'email' in data else None
            tel = data['tel'] if 'tel' in data else None
            iban = data['iban'] if 'iban' in data else None
            state = data['state'] if 'state' in data else None
            city = data['city'] if 'city' in data else None
            zip_code = data['zip'] if 'zip' in data else None
            address = data['address'] if'address' in data else None
            success = update_user_data(acc_id= None,ctr_id=ctr_id,first_name=first_name,last_name=last_name,email=email,phone=tel,iban=iban,acc_state=state,acc_city=city,acc_zip_code=zip_code,acc_address=address)
            if success:
                return redirect(url_for('home'))
            else:
                return render_template('edit_contract.html', user = request.form, contract=request.form,
                                       error='Cant update your Profile')
                
        if request.args.get('contract_id') is not None:
            contract_data = get_contract_data(request.args.get('contract_id'))
            if contract_data:
                response = requests.get(kp_url + "/data/user/", json={'contract_id':contract_data['_id']},cert = mycert, verify=root_ca)
                if not response.status_code == 200:
                    return render_template('edit_contract.html', user = output,contract=request.form,
                                       error='Cant update your Profile')
                user = JSON.loads(response.text)
                print(user)
                return render_template('edit_contract.html', user=user,contract=contract_data)
        return redirect(url_for('home') + '?msg=ici')
    return redirect(url_for('login'))


@app.route('/maintenance/', methods=['GET'])
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
                valid_referrer = urljoin(urljoin(request.url_root, url_for("handle_support_case")),
                                         f"?case-id={case_id}")
                if request.referrer != valid_referrer:
                    # Ensure user requests from support ticket or seriously manipulate request
                    return redirect(url_for('home') + '?msg=invalid')
                with open("./sign_test_key.pem", "rb") as f:
                    priv_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
                cookie_data = {"iss": "msb", "aud": "smartmeter", "device_uuid": str(id),
                                "user_id": user_data["_id"],
                                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=20)}
                encoded = jwt.encode(cookie_data, priv_key, algorithm="RS512")
                red_url_enc = quote(urljoin(request.url_root, url_for("home")), safe="")
                logging.info(f"User [{cookie_data['user_id']}] activated maintenance for "
                                f"device [{cookie_data['device_uuid']}] connected to support case [{case_id}]")
                return redirect(
                    f"{meter_url}/meter/{id}/activate-maintenance/?code={encoded}&next={red_url_enc}")
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
        "device_uuid": "7cba2246-0dbc-4ee0-b551-927736085256",
        "description": "Consumption goes up too fast. User complains about high usage and resulting fees",
        "opened_by": "Deez Nutz",
        "comments": [{"name": "Popi Aram", "comment": "Maybe has to be restarted.", "time": datetime.datetime.now()},
                     {"name": "Will Fit", "comment": "Transfer ticket over to technician",
                      "time": datetime.datetime.now()}]
    }
    return render_template("technician.html", case_data=case_data)

@app.route("/new-contract/", methods=["GET", "POST"])
def new_contract():
    print("i am not atomic", request.environ['peercert'])
    if request.environ['peercert']:
        if True: #if 'date' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'phone' in request.form and 'email' in request.form and 'iban' in request.form and 'state' in request.form and 'city' in request.form and 'zip_code' in request.form and 'address' in request.form and 'em_id' in request.form:
            print("\n\n\n\n",request.form.to_dict())
            _id = request.form['id']
            date = request.form['date']
            iban = request.form['iban']
            state = request.form['state']
            city = request.form['city']
            zip_code = request.form['zip_code']
            address = request.form['address']
            em_id = request.form['em_id']
            #NOTE no more user data saved :)
            c = create_contract(_id, date, iban, state, city, zip_code, address, em_id)
            if c:
                return make_response("successful", 200)
    return make_response("Unauthorized", 401)

@app.route("/new-em/", methods=["GET", "POST"])
def new_em():
    print("i am not atomic")
    data = request.json
    if request.environ['peercert']:
        print("i am atomic", request.environ['peercert'])
        data = request.json
        if True: #if 'date' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'phone' in request.form and 'email' in request.form and 'iban' in request.form and 'state' in request.form and 'city' in request.form and 'zip_code' in request.form and 'address' in request.form and 'em_id' in request.form:
            consumption = data['consumption']
            em_id = data['em_id']
            send_registration_mail(em_id)
            hist_id = data['hist_id']
            if not db_elmo_handler.get_Em_by_id(em_id):
                e = Em(consumption, hist_id, em_id)
                if create_em(e):
                    return make_response("successful", 200)    
            return make_response("internal server error",500)
    return make_response("Unauthorized", 401)

if __name__ == "__main__":
    context = mycert
    ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH,cafile=root_ca)#root_ca)
    ssl_context.load_cert_chain( certfile=context[0], keyfile=context[1], password=None )
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)
