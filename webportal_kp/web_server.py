from flask import Flask, render_template, request, redirect, url_for, make_response, session
from os import urandom, getenv
from database.AccountDB import AccountHandler
from database.InternalDataclasses import Account, Contract


app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
app.config['SESSION_COOKIE_SECURE'] = True
pw = getenv('StromiPW')
username = getenv('StromiUser')
dbname = getenv('StromiDB')
db_handler = AccountHandler(username,pw,dbname)
#todo: login, register, logout logic; fingerprint, css, database, password requirements
#support, "email confirm"

def check_session(uuid):
    
    #checks if uuid exists and is valid returns account data
    if uuid == None:
        return False
    dbu = db_handler.get_account_by_id(uuid)
    if dbu:
        return dbu
    return False

def check_login(username, password):
    if db_handler.get_account_by_username(username):
        #TODO validate pwd hash :P
        return {'uuid':'uuid'}

def check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
    contract = Contract(em_id,"date","info",[0],0,0)
    acc = Account(username,password, "salt",first_name,last_name,email,iban,phone,city,zip_code,address,contract)
    #Check if username is already in use, TODO check for the rest of bs
    if db_handler.get_account_by_username(acc.username):
        return False
    
    return db_handler.create_account()

def update_user_data(username, email, phone, iban, id = None):#PLASE GIVE ME ID PLEAAAAAASE
    #if new requested username is already reserved, dont update!
    if db_handler.get_account_by_username(username):
        return False
    #TODO please i want id of current active user to update GIVE ME
    #this is theoretically possible but i really dont advise it
    #db_handler.update_account_by_username(old_username, {"username":username, "email": email, "phone":phone, "iban": iban})#TODO do better wtf is this
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

@app.route('/register', methods=['GET','POST'])
def register():
    #{"username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69}
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
        if check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
            return redirect(url_for(login))
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