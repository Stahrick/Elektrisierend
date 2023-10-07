from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)
app.secret_key = 'hihihihihihihi'

#todo: login, register, logout logic; fingerprint, 

@app.route('/login', methods=['GET','POST'])
def login():
    msg = ''
    return render_template('login.html', testo='thihihi')

@app.route('/logout', methods=['GET','POST'])
def logout():
    msg = ''
    return render_template('login.html', testo='thihihi')

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template('register.html', testo='ich ficke deine mutter yo')

@app.route('/home', methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/profile', methods=['GET','POST'])
def profile():
    return render_template('profile.html', username='test', z_id=123789, z_current=666, iban=3)

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    return render_template('edit_profile.html', username='test', z_id=123789, z_current=666, iban=3)

print('running')