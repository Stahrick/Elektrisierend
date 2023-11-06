from flask import Flask, render_template, request, redirect, url_for, make_response, session
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.ContractDB import ContractHandler
from database.EMDB import EmHandler
from database.HistDataDB import HistDataHandler
from database.InternalDataclasses import Account, Contract
from dotenv import load_dotenv

from views.metercommunication import meter
from views.electricityprovider import provider


app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True

load_dotenv()
pw = getenv('MSBPW')
username = getenv('MSBUser')
dbname = getenv('MSBDB')
db_acc_handler = AccountHandler(username,pw,dbname)
db_ctr_handler = ContractHandler(username,pw,dbname)
db_elmo_handler = EmHandler(username,pw,dbname)
db_hdt_handler = HistDataHandler(username,pw,dbname)

app.register_blueprint(meter, url_prefix="/meter")
app.register_blueprint(provider, url_prefix="/provider")
#todo: login, register, logout logic; fingerprint, css, database, password requirements
#support, "email confirm"
#

def check_session(uuid):
    #checks if uuid exists and is valid returns account data
    if uuid == None:
        return False
    acc = db_acc_handler.get_account_by_id(uuid)
    if acc:
        return acc
    
    return False

def check_login(username, password):
    res = db_acc_handler.get_account_by_username(username)[0]
    if res:
       return {'uuid':res['_id'], 'role': res['role']}
    return {'uuid':'uuid', 'role': 'technician'}

def check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
    contract = Contract(em_id,"date","info",[0],"0","0")
    acc = Account(username,password, 123,first_name,last_name,email,iban,phone,city,zip_code,address,contract)
    #Check if username is already in use, TODO check for the rest of bs
    if db_acc_handler.get_account_by_username(acc.username):
        return False
    res = db_acc_handler.create_account()
    return True #res

#updates account data by given fields, ignores params all if data is given directly
#TODO please test
def update_user_data(_id, role = None,  
                     username  = None,  
                     pw_hash = None,  pw_salt = None,  
                     first_name = None,  last_name = None,  
                     email  = None,  phone  = None,  
                     city  = None,  zip_code = None,  
                     address  = None,  contract_id = None, 
                     data : dict = None):
    param = locals()
    print(type(param))
    del(param['_id'])
    if db_acc_handler.get_account_by_username(username):
        return False    
    if 'data' in param:
        return db_acc_handler.update_account_by_id(_id,data)
    else:
        return db_acc_handler.update_account_by_id(_id,param)
def update_contract_data(_id, date = None, personal_info = None, iban = None, em_id = None, state = None, city = None, zip_code = None, address = None, data : dict = None):
    param = locals()
    print(type(param))
    del(param['_id'])
    if 'data' in param:
        return db_acc_handler.update_account_by_id(_id,data)
    else:
        return db_acc_handler.update_account_by_id(_id,param)

def get_contract_data(contract_id):
    res = db_ctr_handler.get_contract_by_id(contract_id)
    print(res)
    return {"uuid": 123, "username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "state":"Germany", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69, "contract_id": "\{\{ 7*7 \}\}"}

def get_ems_by_contract():
    dbres = db_ctr_handler.get_all()
    l1,l2,l = list(),list(),list()
    for i,r in enumerate(dbres):
        l1.append(r['em_id'])#ich hasse konrad
        l2.append(r['_id'])
    return [l1,l2]

def check_em_id(id):
    res = db_elmo_handler.get_Em_by_id(id)
    if res:
        return True
    return False

def activate_maintenance(id):
    return True

@app.route('/login', methods=['GET','POST'])
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

@app.route('/logout', methods=['GET','POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    session.clear()
    return response

@app.route('/home', methods=['GET','POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if session.get('role')=='office':
            if request.args.get('msg')=='ici':
                error = 'your contract ID is invalid'
                return render_template('office.html', msg=error)
            return render_template('office.html')
        elif session.get('role')=='technician':
            msg = request.args.get('msg')
            if msg is not None:
                if msg=='invalid':
                    msg = 'The selected Elecricity Meter could\'nt be set to maintenance mode'
                if msg=='active':
                    msg = 'Elecricity Meter: '+ request.args.get('id') + ' has been set to maintenance mode'
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
                return render_template('show_contract.html', contract_id=contract_data['contract_id'], em_id=contract_data['em_id'], em_reading = contract_data['em_reading'], state = contract_data['state'], zip_code = contract_data['zip_code'], city = contract_data['city'], address = contract_data['address'], iban = contract_data['iban'], phone = contract_data['phone'], email = contract_data['email'], username = contract_data['username'], first_name = contract_data['first_name'], last_name = contract_data['last_name'])
            else:
                #das lässt gerade template injections zu
                return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/edit_contract', methods=['GET','POST'])
def edit_contract():
    user_data = check_session(session.get('uuid'))
    if user_data:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            #checks if post request with correct data value pairs
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            iban = request.form['iban']
            if update_user_data(user_data['_id'],username = username,email= email,phone= phone):
                #trys to update database and redirects to profile if it did
                #updates values for account that owns the cookie
                return redirect(url_for('profile'))
            else:
                #returns error if it cant update
                return render_template('edit_profile', username=username, email=email, phone=phone, iban=iban, error='Cant update your Profile')
        if request.args.get('contract_id') is not None:
            contract_data = get_contract_data(request.args.get('contract_id'))
            if contract_data:
                return render_template('edit_contract.html', contract_id=contract_data['contract_id'], em_id=contract_data['em_id'], em_reading = contract_data['em_reading'], state = contract_data['state'], zip_code = contract_data['zip_code'], city = contract_data['city'], address = contract_data['address'], iban = contract_data['iban'], phone = contract_data['phone'], email = contract_data['email'], username = contract_data['username'], first_name = contract_data['first_name'], last_name = contract_data['last_name'])
        return redirect(url_for('home')+'?msg=ici')
    return redirect(url_for('login'))

@app.route('/maintenance', methods=['GET'])
def maintenance():
    user_data = check_session(session.get('uuid'))
    if user_data:
        id = request.args.get('id')
        if session.get('role')=='technician' and id is not None:
            if check_em_id(id):
                if activate_maintenance(id):
                    return redirect(url_for('home')+'?msg=active&id='+id)
    else:
        return redirect(url_for('home')+'?msg=invalid')

app.run(debug=True, port=5000)