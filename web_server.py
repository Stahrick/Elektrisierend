from flask import Flask, render_template, request, redirect, url_for, make_response


app = Flask(__name__)
app.secret_key = 'hihihihihihihi'

#todo: login, register, logout logic; fingerprint, css, database

def check_session(request_data):
    uuid = request_data.cookies.get('UUID')
    #checks if uuid exists and returns account data
    if uuid == None:
        return False
    if "test" in uuid:
        return [1,2,3]

    return False

def check_login(username, password):
    return True

def check_register(username, password, email):
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

    return render_template('login.html', error='invalid login')

@app.route('/logout', methods=['GET','POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('UUID')
    return response

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if check_register(username, password, email):
            return redirect(url_for(login))
    return render_template('register.html', error='invalid data')

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
        return render_template('profile.html', username='test', z_id=123789, z_current=666, iban=3)
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    user_data = check_session(request)
    if user_data:
        return render_template('edit_profile.html', username='test', z_id=123789, z_current=666, iban=3)
    return redirect(url_for('login'))

print('running')