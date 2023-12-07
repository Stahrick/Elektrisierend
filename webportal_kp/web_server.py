from flask import Flask, render_template, request, redirect, url_for, make_response, session
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.ContractDB import ContractHandler
from database.EmDBkp import EmHandler
from database.InternalDataclasses import Account, Contract
from dotenv import load_dotenv
import requests
from datetime import datetime
import ssl
import werkzeug.serving
from passlib.hash import argon2
from password_validation import PasswordPolicy

from config import msb_url, meter_url

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True

load_dotenv()
pw = getenv('StromiPW')
username = getenv('StromiUser')
dbname = getenv('StromiDB')
db_acc_handler = AccountHandler(username,pw,dbname)
db_ctr_handler = ContractHandler(username,pw,dbname)
db_elmo_handler = EmHandler(username, pw, dbname)
pw_policy = PasswordPolicy(lowercase=12,uppercase=1,symbols=1,numbers=1,whitespace=1,min_length=16)

#TODO: login, register, logout logic; fingerprint, css, database, password requirements
#support, "email confirm"

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
        if x509_binary:
            x509 = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
            environ['peercert'] = x509
            return environ
        environ['peercert'] = None
        return environ

def check_session(uuid):
    #checks if uuid exists and is valid returns account data
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
            if argon2.verify(password,res['pw_hash']):
                return {'_id': res['_id']}
        except Exception as e:
            return None
    return None

def check_register(username, pw, 
                    first_name, last_name, 
                    email , phone , 
                    acc_state, acc_city , acc_zip_code, 
                    acc_address,
                    personal_info, 
                    iban, em_id, 
                    ctr_state, ctr_city, 
                    ctr_zip_code, ctr_address, date
                    ) -> bool:
    
    #Check if username is already in use, or if em_id is already in used by another contract
    if not pw_policy.validate(pw):
        missed_reqs = pw_policy.test_password(pw)#TODO how do i get this out of here
        return False
    print("hallo")
    if db_acc_handler.get_account_by_username(username) or db_elmo_handler.get_Em_by_id(em_id):
        return False
    #TODO check for em_id?
    #TODO insert current date or what else
    contract = Contract(date,personal_info,iban,em_id,ctr_state,ctr_city,ctr_zip_code,ctr_address)
    contract_db = db_ctr_handler.create_contract(contract)
    a2pw = argon2.hash(pw)
    print("argon hashing")
    if contract_db:
        print("contract_db true")
        acc = Account(username,a2pw,first_name,last_name,email,phone,acc_state,acc_city,acc_zip_code,acc_address,contract_db['id'])
        acc_db = db_acc_handler.create_account(acc)
        if acc_db:
            print("acc_db")
            return True #NOTE return acc_db maybe?
    return False
    
def update_user_data(acc_id, ctr_id,
                     username  = None, pw = None,
                     first_name = None, last_name = None, 
                     email  = None, phone  = None, 
                     acc_state = None,
                     acc_city  = None, acc_zip_code = None, 
                     acc_address  = None, acc_contract_id = None, 
                     acc_data : dict = None, 
                     personal_info = None, 
                     iban = None, em_id = None, 
                     ctr_state = None, ctr_city = None, 
                     ctr_zip_code = None, ctr_address = None, 
                     ctr_data : dict = None,
                     ) -> bool:
    if pw:
        if not pw_policy.validate(pw):
            missed_reqs = pw_policy.test_password(pw)#TODO how do i get this out of here
            return False
    pw = argon2.hash(pw)#should only be accessible if already authenticated so np
    b1 = update_acc_data(acc_id, username, pw, first_name, last_name, email, phone, acc_state, acc_city, acc_zip_code, acc_address, acc_contract_id, acc_data)
    b2 = update_contract_data(ctr_id, personal_info, iban, em_id, ctr_state, ctr_city, ctr_zip_code, ctr_address, ctr_data)
    if b1 and b2:
        return True
    return False
def update_acc_data(_id,username  = None, pw = None, first_name = None, last_name = None, email  = None, phone  = None, state = None, city  = None, zip_code = None, address  = None, contract_id = None, data : dict = None) -> bool:
    param = locals()
    if param:
        del(param['_id'])
        if db_acc_handler.get_account_by_username(username):
            return False    
        if 'data' in param:
            return db_acc_handler.update_account_by_id(_id,data)
        else:
            return db_acc_handler.update_account_by_id(_id,param)
    return True
    
def update_contract_data(_id, date = None, personal_info = None, iban = None, em_id = None, state = None, city = None, zip_code = None, address = None, data : dict = None):
    param = locals()
    if param:
        del(param['_id'])
        if 'data' in param:
            return db_acc_handler.update_account_by_id(_id,data)
        else:
            return db_acc_handler.update_account_by_id(_id,param)
    return True

def _create_em(em_id):
    # TODO put meter into db
    return True

def create_em():
    em_id = requests.post(meter_url + "/meter/order/", json={}, headers={"X-Client-Certificate": "123"}).text
    if _create_em(em_id):
        return True   
    return False

def create_msb_contract(date, first_name, last_name, email, iban, phone, state, city, zip_code, address, em_id):
    response = requests.post("https://localhost:5000/new-contract/", files={"date":(None, date), "first_name":(None, first_name), "last_name":(None, last_name), "email":(None, email), "iban":(None, iban), "phone":(None, phone), "state":(None, state), "city":(None, city), "zip_code":(None, zip_code), "address":(None, address), "em_id":(None, em_id) }, headers={"X-Client-Certificate":"123"}, verify=False)
    print(response)
    if response.status_code == 200:
        return True
    return False

@app.route('/login/', methods=['GET','POST'])
def login():
    print([i for i in request.form])
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
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

@app.route('/logout', methods=['GET','POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    session.clear()
    return response

@app.route('/register/', methods=['GET','POST'])
def register():
    #{"username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69}
    print( [i for i in  request.form])
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'iban' in request.form and 'phone' in request.form and 'city' in request.form and 'zip_code' in request.form and 'address' in request.form and 'em_id' in request.form and 'state' in request.form:
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
        personal_info = "Mutterficker"
        if not em_id:
            em_id = create_em()
            if not em_id:
                return render_template('register.html', error='error while creating electricity meter, please try again')
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print("ich bin gekommen \n\n\n")
        if check_register(username, password, first_name, last_name, email, phone, state, city, zip_code, address, personal_info, iban, em_id, state, city, zip_code, address, date):
            create_msb_contract(date, first_name, last_name, email, iban, phone, state, city, zip_code, address, em_id)
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='invalid data')
    return render_template('register.html')

@app.route('/forgot-password/', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    elif request.method == 'POST':
        username = request.form.get("username", "")
        code = request.form.get("code", "")
        new_pw = request.form.get("password", "")
        if "" in {username, code, new_pw}:
            return render_template('forgot_password.html', username=username, code=code)
        else:
            # Always redirect to deny account enumeration
            if code == "31":
                # TODO Set new password on account
                pass
            return redirect(url_for('login'))
@app.route('/home/', methods=['GET','POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/profile/', methods=['GET','POST'])
def edit_profile():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            #checks if post request with correct data value pairs
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            iban = request.form['iban']
            if update_user_data(username, email, phone, iban):
                #trys to update database and redirects to profile if it did
                #updates values for account that owns the cookie
                return redirect(url_for('profile'))
            else:
                #returns error if it cant update
                return render_template('edit_profile', profile=user_data, error='Cant update your Profile')
        return render_template('edit_profile.html', profile=user_data)
    return redirect(url_for('login'))

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    context = ('localhost.crt', 'localhost.key')
    ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH,cafile=context[0] )
    ssl_context.load_cert_chain( certfile=context[0], keyfile=context[1], password=None )
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(host='0.0.0.0', port=4000, debug=True, ssl_context=context)