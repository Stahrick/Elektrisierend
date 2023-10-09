from flask import Flask, render_template, request, redirect, url_for, make_response


app = Flask(__name__)

#todo: login, register, logout logic; fingerprint, css, database, password requirements

def check_session(request_data):
    uuid = request_data.cookies.get('UUID')
    #checks if uuid exists and is valid returns account data
    if uuid == None:
        return False
    if "test" in uuid:
        return {"username": "testo", "first_name": "Shadow", "last_name": "Sama", "email":"cum@me.com", "iban":"DE123654", "phone":"+49112", "city":"Madenheim", "zip_code":"69069", "address":"Wallstreet 3", "em_id":"DEADBEEF4269", "em_reading":911.69}

    return False

def check_login(username, password):
    return True

def check_register(username, password, first_name, last_name, email, iban, phone, city, zip_code, address, em_id):
    return True

def update_user_data(username, email, phone, iban):
    return True

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        valid = check_login(username, password)
        if valid:
            response = make_response(redirect(url_for('home')))
            response.set_cookie('UUID', username+"test"+password)
            return response
        else:
            return render_template('login.html', error='invalid login')
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('UUID')
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
    user_data = check_session(request)
    if user_data:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    user_data = check_session(request)
    if user_data:
        return render_template('profile.html', first_name=user_data['first_name'], last_name=user_data['last_name'], em_id=user_data['em_id'], em_reading=user_data['em_reading'], iban=user_data['iban'], phone=user_data['phone'], email=user_data['email'] )
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    user_data = check_session(request)
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
                return render_template('edit_profile', username=username, email=email, phone=phone, iban=iban, error='Cant update your Profile')
        return render_template('edit_profile.html', username=user_data['username'], email=user_data['email'], phone=user_data['phone'], iban=user_data['iban'])
    return redirect(url_for('login'))

print('running')