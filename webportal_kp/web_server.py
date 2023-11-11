from flask import Flask, render_template, request, redirect, url_for, make_response, session
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.ContractDB import ContractHandler
from database.InternalDataclasses import Account, Contract
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True

load_dotenv()
pw = getenv('StromiPW')
username = getenv('StromiUser')
dbname = getenv('StromiDB')
db_acc_handler = AccountHandler(username,pw,dbname)
db_ctr_handler = ContractHandler(username,pw,dbname)

#todo: login, register, logout logic; fingerprint, css, database, password requirements
#support, "email confirm"

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
       if password == res[0]['pw_hash']: #TODO hash
           return {'_id': res[0]['_id']}
    return None

def check_register(username, 
                    pw_hash, pw_salt, 
                    first_name, last_name, 
                    email , phone , 
                    acc_state, acc_city , acc_zip_code, 
                    acc_address,
                    personal_info, 
                    iban, em_id, 
                    ctr_state, ctr_city, 
                    ctr_zip_code, ctr_address,
                    ) -> bool:
    
    #Check if username is already in use, TODO check for the rest of bs
    if db_acc_handler.get_account_by_username(username):
        return False
    #TODO check for em_id?
    #TODO insert current date or what else
    contract = Contract("date",personal_info,iban,em_id,ctr_state,ctr_city,ctr_zip_code,ctr_address)
    contract_db = db_ctr_handler.create_contract(contract)
    if contract_db:
        if not pw_salt: pw_salt = 123 #NOTE remove when implemented
        acc = Account(username,pw_hash, pw_salt,first_name,last_name,email,phone,acc_state,acc_city,acc_zip_code,acc_address,contract_db['_id'])
        acc_db = db_acc_handler.create_account(acc)
        if acc_db:
            return True #NOTE return acc_db maybe?
    
def update_user_data(acc_id, ctr_id,
                     username  = None, 
                     pw_hash = None, pw_salt = None, 
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
    b1 = update_acc_data(acc_id, username, pw_hash, pw_salt, first_name, last_name, email, phone, acc_state, acc_city, acc_zip_code, acc_address, acc_contract_id, acc_data)
    b2 = update_contract_data(ctr_id, personal_info, iban, em_id, ctr_state, ctr_city, ctr_zip_code, ctr_address, ctr_data)
    if b1 and b2:
        return True
    return False
def update_acc_data(_id,username  = None, pw_hash = None, pw_salt = None, first_name = None, last_name = None, email  = None, phone  = None, state = None, city  = None, zip_code = None, address  = None, contract_id = None, data : dict = None) -> bool:
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


@app.route('/login', methods=['GET','POST'])
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

@app.route('/register', methods=['GET','POST'])
def register():
    #{"username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69}
    print( [i for i in  request.form])
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'iban' in request.form and 'phone' in request.form and 'city' in request.form and 'zip_code' in request.form and 'address' in request.form and 'em_id' in request.form:
        
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
        print(iban)
        if check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='invalid data')
    return render_template('register.html')

@app.route('/home', methods=['GET','POST'])
def home():
    user_data = check_session(session.get('uuid'))
    if user_data:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    user_data = check_session(session.get('uuid'))
    if user_data:
        return render_template('profile.html', first_name=user_data['first_name'], last_name=user_data['last_name'], em_id=user_data['em_id'], em_reading=user_data['em_reading'], iban=user_data['iban'], phone=user_data['phone'], email=user_data['email'] )
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET','POST'])
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
                return render_template('edit_profile', username=username, email=email, phone=phone, error='Cant update your Profile')
        return render_template('edit_profile.html', username=user_data['username'], email=user_data['email'], phone=user_data['phone'], iban=user_data['iban'])
    return redirect(url_for('login'))

app.run(debug=True, port=4000)