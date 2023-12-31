from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask_wtf.csrf import CSRFProtect
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.ContractDB import ContractHandler
from database.EmDBkp import EmHandler
from database.HistDB import HistDataHandler
from database.InternalDataclasses import Account, Contract, Em, HistData
from data_validation import DataValidator
from dotenv import load_dotenv
import requests
from datetime import datetime
import ssl
import werkzeug.serving
from passlib.hash import argon2
from password_validation import PasswordPolicy

from config import msb_url, meter_url, mycert, root_ca
import OpenSSL
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True
csrf = CSRFProtect(app)
load_dotenv()
pw = getenv('StromiPW')
username = getenv('StromiUser')
dbname = getenv('StromiDB')
db_acc_handler = AccountHandler(username, pw, dbname)
db_ctr_handler = ContractHandler(username, pw, dbname)
db_elmo_handler = EmHandler(username, pw, dbname)
db_hist_handler = HistDataHandler(username, pw, dbname)
pw_policy = PasswordPolicy(min_length=12, min_entropy=0.0000001)


# TODO: login, register, logout logic; fingerprint, css, database, password requirements
# support, "email confirm"
class PeerCertWSGIRequestHandler(werkzeug.serving.WSGIRequestHandler):
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
        if x509_binary:
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, x509_binary)
            environ['peercert'] = x509
            return environ
        environ['peercert'] = None
        return environ


def check_session(uuid):
    # checks if uuid exists and is valid returns account data
    if uuid == None:
        return False
    dbu = db_acc_handler.get_account_by_id(uuid)
    if dbu:
        return dbu
    return False


def check_login(username, password):
    res = db_acc_handler.get_account_by_username(username)
    if res and res[0]:
        res = res[0]
        print(res)
        try:
            if argon2.verify(password, res['pw_hash']):
                return {'_id': res['_id']}
        except Exception as e:
            return None
    return None


def check_register(username, pw,
                   first_name, last_name,
                   email, phone,
                   acc_state, acc_city, acc_zip_code,
                   acc_address,
                   iban, em_id,
                   ctr_state, ctr_city,
                   ctr_zip_code, ctr_address, date
                   ) -> (bool, list):
    invalid_data = []
    if not DataValidator.is_valid_first_name(first_name):
        invalid_data.append("Invalid first name")
    if not DataValidator.is_valid_last_name(last_name):
        invalid_data.append("Invalid last name")
    if not DataValidator.is_valid_email(email):
        invalid_data.append("Invalid email")
    if not DataValidator.is_valid_state(acc_state):
        invalid_data.append("Invalid state")
    if not DataValidator.is_valid_address(acc_address):
        invalid_data.append("Invalid address")
    if not DataValidator.is_valid_iban(iban):
        invalid_data.append("Invalid iban")
    if len(em_id) > 0 and not DataValidator.is_valid_em_id(em_id):
        invalid_data.append("Invalid meter id")
    if not DataValidator.is_valid_phone_number(phone):
        invalid_data.append("Invalid phone number")

    # Check if username is already in use, or if em_id is already in used by another contract
    if not pw_policy.validate(pw):
        missed_reqs = pw_policy.test_password(pw)  # TODO how do i get this out of here
        invalid_data.extend(missed_reqs)
    print("hallo")
    if db_acc_handler.get_account_by_username(username) or db_elmo_handler.get_Em_by_id(em_id):
        invalid_data.append("Occupied username")

    if invalid_data:
        return False, invalid_data
    # TODO check for em_id?
    # TODO insert current date or what else
    a2pw = argon2.hash(pw)

    if not em_id:
        em_id = create_em()
    if not em_id:
        return False, []
    contract = Contract(date, iban, em_id, ctr_state, ctr_city, ctr_zip_code, ctr_address)
    contract_db = db_ctr_handler.create_contract(contract)
    print(contract_db)
    if not contract_db:
        return False, []
    print("contract_db true")
    acc = Account(username, a2pw, first_name, last_name, email, phone, acc_state, acc_city, acc_zip_code, acc_address,
                  contract_db['id'])
    acc_db = db_acc_handler.create_account(acc)
    if acc_db:
        create_msb_contract(date, iban, em_id, ctr_state, ctr_city, ctr_zip_code, ctr_address, contract_db['id'])
        print("acc_db")
        return True, []  # NOTE return acc_db maybe?


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
    if first_name and not DataValidator.is_valid_first_name(first_name):
        return False
    if last_name and not DataValidator.is_valid_last_name(last_name):
        return False
    if email and not DataValidator.is_valid_email(email):
        return False
    if acc_state and not DataValidator.is_valid_state(acc_state):
        return False
    if acc_address and not DataValidator.is_valid_address(acc_address):
        return False
    if iban and not DataValidator.is_valid_iban(iban):
        return False
    if em_id and not DataValidator.is_valid_em_id(em_id):
        return False
    if phone and not DataValidator.is_valid_phone_number(phone):
        return False
    if not ctr_id:
        acc = db_acc_handler.get_account_by_id(acc_id)
        if acc:
            ctr_id = acc['contract_id']
    if pw:
        if not pw_policy.validate(pw):
            missed_reqs = pw_policy.test_password(pw)  # TODO how do i get this out of here
            return False
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
    param = {k: v for k, v in params.items() if v is not None}
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


def create_em():
    em_id = requests.post(meter_url + "/meter/order/", json={}, cert=mycert, verify=root_ca).text
    h = HistData([])
    e = Em(0, h._id, _id=em_id)
    if db_elmo_handler.create_Em(e):
        if create_hist_data(h._id):
            res = create_msb_ems(e)
            print(res)
            return em_id
    return None


def create_hist_data(hist_id):
    return db_hist_handler.create_HistData(HistData([], _id=hist_id))


def create_msb_contract(date, iban, em_id, state, city, zip_code, address, contract_id):
    response = requests.post(f"{msb_url}/new-contract/", files={"id": (None, contract_id),"date": (None, date), "iban": (None, iban),
                                                                "state": (None, state), "city": (None, city),
                                                                "zip_code": (None, zip_code),
                                                                "address": (None, address), "em_id": (None, em_id)},
                             cert=mycert, verify=root_ca)
    print(response)
    if response.status_code == 200:
        return response.text
    return False


def create_msb_ems(em):
    consumption = em.em_consumption
    hist_id = em.hist_id
    em_id = em._id
    return requests.post(f"{msb_url}/new-em/", json={"consumption": consumption, "hist_id": hist_id, "em_id": em_id},
                         cert=mycert, verify=root_ca)


def get_hist_data(em_id):
    em = db_elmo_handler.get_Em_by_id(em_id)
    h_data = db_hist_handler.get_HistData_by_id(em['hist_id'])
    return h_data


@app.route('/login/', methods=['GET', 'POST'])
def login():
    print([i for i in request.form])
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        app.logger.info(str(request.form))
        username = request.form['username']
        password = request.form['password']
        valid = check_login(username, password)
        if valid:
            print("valid")
            response = make_response(redirect(url_for('home')))
            session['uuid'] = valid['_id']
            return response
        else:
            print("invalid")
            session.clear()
            return render_template('login.html', error='invalid login')
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    session.clear()
    return response


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # {"username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69}
    print([i for i in request.form])
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'iban' in request.form and 'phone' in request.form and 'city' in request.form and 'zip_code' in request.form and 'address' in request.form and 'em_id' in request.form and 'state' in request.form:
        app.logger.info(str(request.form))
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        iban = request.form['iban']
        phone = request.form['phone']
        city = request.form['city']
        zip_code = request.form['zip_code']
        address = request.form['address']
        em_id = request.form['em_id']
        state = request.form['state']
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        check = check_register(username, password, first_name, last_name, email, phone, state, city, zip_code, address, iban,
                          em_id, state, city, zip_code, address, date)
        if check[0]:
            return redirect(url_for('login'))
        else:
            return render_template('register.html', errors=check[1], sub_data=request.form)
    return render_template('register.html', sub_data={})


@app.route('/forgot-password/', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    elif request.method == 'POST':
        app.logger.info(str(request.form))
        username = request.form.get("username", "")
        code = request.form.get("code", "")
        new_pw = request.form.get("password", "")
        if "" in {username, code, new_pw}:
            return render_template('forgot_password.html', username=username, code=code)
        else:
            # Always redirect to deny account enumeration
            if code == "31":
                if pw_policy.validate(pw):
                    user = db_acc_handler.get_account_by_username(username)[0]
                    print(user)
                    if update_user_data(user['_id'],pw = new_pw):
                        return redirect(url_for('login'))
                    # TODO Set new password on account
                    pass
            return redirect(url_for('login'))


@app.route('/home/', methods=['GET', 'POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        ctr = db_ctr_handler.get_contract_by_id(user_data['contract_id'])
        print(ctr)
        print()
        em = db_elmo_handler.get_Em_by_id(ctr['em_id'])
        print(em)
        print()
        hist_data =  [int(i) if i else 0 for i in ((get_hist_data(ctr['em_id'])['data'])).strip('][').split(', ')]
        if len(hist_data)>12:
            hist_data = hist_data[-12:]
        forecast = hist_data[-1]-hist_data[-2] if len(hist_data) > 1 else "not enough data to calculate"
        resp = make_response(render_template('home.html',  forecast = forecast, h_data=hist_data, em=em))
        resp.headers['charset'] = 'utf-8'
        return resp
    return redirect(url_for('login'))


@app.route('/profile/', methods=['GET', 'POST'])
def edit_profile():
    user_data = check_session(session.get('uuid'))
    print(user_data)
    if user_data:
        if request.method == 'POST' and request.form:
            # checks if post request with correct data value pairs
            app.logger.info(str(request.form))
            first_name = request.form.get('first_name') if request.form.get('first_name') else None
            last_name = request.form.get('last_name') if request.form.get('last_name') else None
            email = request.form.get('email') if request.form.get('email') else None 
            phone = request.form.get('phone') if request.form.get('phone') else None 
            iban = request.form.get('iban') if request.form.get('iban') else None 
            if not update_user_data(user_data['_id'], first_name=first_name, last_name=last_name, email=email, phone=phone, iban=iban):
                print("HAHAHAH ERROR HANDLING ;)\n\n\n\n\n\n\n")
                ctr = db_ctr_handler.get_contract_by_id(user_data['contract_id'])
                em = db_elmo_handler.get_Em_by_id(ctr['em_id'])
                return render_template('edit_profile.html', profile=user_data, ctr=ctr, em=em, errors=['Error: Invalid Data input'])
            return redirect(url_for('edit_profile'))
        ctr = db_ctr_handler.get_contract_by_id(user_data['contract_id'])
        em = db_elmo_handler.get_Em_by_id(ctr['em_id'])
        return render_template('edit_profile.html', profile=user_data, ctr=ctr, em=em)
    return redirect(url_for('login'))


@app.route('/data/', methods=['POST'])
def accept_em_data():
    if request.environ['peercert']:
        if request.method == 'POST' and 'em' in request.form and 'consumption' in request.form:
            app.logger.info(str(request.form))
            r_em = request.form
            em = db_elmo_handler.get_Em_by_id(r_em['_id'])
            if em:
                h_data_old = db_hist_handler.get_HistData_by_id(em['hist_id'])
                em.em_consumption = request.form['consumption']
                data = h_data_old['data'].append(em.em_consumption)
                success = db_elmo_handler.update_Em_by_id(r_em['_id'], {"em_consumption": request.form['consumption']})
                success2 = db_hist_handler.update_HistData_by_id(em['hist_id'], {"data": data})
                if success and success2:
                    return
            else:  # create, dont care
                e = Em(None, r_em['consumption'], None)
                em = db_elmo_handler.create_Em(e)
                if em:
                    h = HistData([], _id=em.hist_id)
                    h_data = db_hist_handler.create_HistData(h)
                    print(h_data)
                    if h_data:
                        return make_response("successful", 200)
        return make_response("internal server error", 500)
        # always great success
        # return False


@app.route('/data/user/', methods=['GET','POST'])
@csrf.exempt
def get_user_for_msb():
    if request.method == 'POST' and request.environ["peercert"]:
        input = request.json
        app.logger.info(str(request.json))
        if 'contract_id' in input:
            acc = db_acc_handler.get_account_by_ctr_id(input['contract_id'])
            if acc and acc[0]:
                acc = acc[0]
            ctr_id = input.pop('contract_id')
            print(input)

            first_name = input['first_name'] if'first_name' in input else None
            last_name = input['last_name'] if 'last_name' in input else None
            email = input['email'] if'email' in input else None
            tel = input['tel'] if 'tel' in input else None
            iban = input['iban'] if 'iban' in input else None
            state = input['state'] if 'state' in input else None
            city = input['city'] if 'city' in input else None
            zip_code = input['zip'] if 'zip' in input else None
            address = input['address'] if'address' in input else None
            success = update_user_data(acc_id=acc['_id'],ctr_id=ctr_id,first_name=first_name,last_name=last_name,email=email,phone=tel,iban=iban,acc_state=state,acc_city=city,acc_zip_code=zip_code,acc_address=address)
            if success:
                return acc #thats not the updated user
        else:
            return make_response("no",404)
        return make_response("no",500)

    if request.method == 'GET' and 'contract_id' in request.json and request.environ['peercert']:
        print(1)
        input = request.json
        app.logger.info(str(request.json))
        print(2)
        print(input['contract_id'])
        user = db_acc_handler.get_account_by_ctr_id(input['contract_id'])
        print(3)
        print(user)
        if user and user[0]:
            user = user[0]
        else:
            return make_response("1internal server error", 500)
        print(user)
        return user
    return make_response("internal server error", 500)

@app.route('/', methods=["GET"])
def blank():
    user_data = check_session(session.get('uuid'))
    if user_data:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/impressum', methods=["GET"])
def impressum():
    return render_template('impressum.html')

if __name__ == "__main__":
    context = mycert
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=root_ca)
    ssl_context.load_cert_chain(certfile=context[0], keyfile=context[1], password=None)
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(host='0.0.0.0', port=4000, debug=False, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)
