from flask import Flask, render_template, request, redirect, url_for, make_response


app = Flask(__name__)
app.secret_key = 'hihihihihihihi'

#todo: login, register, logout logic; fingerprint, 

def check_session(request_data):
    uuid = request_data.cookies.get('UUID')
    #checks if uuid exists and returns account data
    if uuid == None:
        return False
    if "test" in uuid:
        return [1,2,3]

    return False

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        valid = True
        if valid:
            response = make_response(redirect(url_for('home')))
            response.set_cookie('UUID', username+"test"+password)
            return response

    return render_template('login.html', testo='thihihi')

@app.route('/logout', methods=['GET','POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('UUID')
    return response

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template('register.html', testo='ich ficke deine mutter yo')

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