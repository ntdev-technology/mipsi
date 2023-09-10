from flask import Flask, flash, render_template, send_file, redirect, request
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from termcolor import colored
from datetime import datetime
import subprocess
import threading
import sqlite3
import bcrypt
import os

__version__ = '1.0.0'


def getDBConn(db: str) -> sqlite3.Connection:
	conn = sqlite3.connect(f'db/{db}.db')
	return conn
	
def createPwHash(password: str) -> str:
	salt = bcrypt.gensalt()
	hashpw = bcrypt.hashpw(password.encode('utf-8'), salt)
	shashpw = f'{salt.decode("utf-8")}|{hashpw.decode("utf-8")}'
	return shashpw

# def checkPw(username, password) -> bool:
# 	conn = getDBConn('users')
# 	cur = conn.cursor()
# 	try:
# 		shash: str = cur.execute('SELECT passwordhash FROM users WHERE username=?', (username,)).fetchall()[0][0]
# 		salt, hash = shash.split('|')
# 		pwhash = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
# 	except: return False
# 	if  pwhash == hash:
# 		return True
# 	else:
# 		return False

def checkPw(dbpw: str, ippw: str):
	salt, hash = dbpw.split('|')
	pwhash = bcrypt.hashpw(ippw.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
	if hash == pwhash:
		return True
	else:
		return False


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba74a4e1a84eddcc42742bb1e0f2a80abe10ad165b010855'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(os.getcwd()+"/db/users.db")}'
db = SQLAlchemy()
db.init_app(app)
loginmng = LoginManager()
loginmng.init_app(app)

with app.app_context():
	db.create_all()



#-----------
# endpoints

@app.route('/')
def home():
	return redirect('/login')



@app.route('/login', methods=['GET', 'POST'])
def login():
	match request.method:
		case 'GET':
			return render_template('login.html')
		case 'POST':
			try:
				usr = User.query.filter_by(
					username=request.form['username']).first()
				if checkPw(usr.passhash, request.form['password']):
					login_user(usr)
					print(f"{request.remote_addr} - - {datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')} " + colored(f'"USER "{usr.username}" LOGGED IN', 'magenta'))
					return redirect('/dashboard')
				else:
					flash('Password Incorrect')
					return render_template('/login.html')	
			except Exception as e:
				print(e)
				flash('Username Invalid')
				return render_template('/login.html')


			...
			# valid = 'login succesfill' if checkPw(request.form['username'], request.form['password']) else 'login failed'
			# return render_template('login.html', status=valid)
		

@app.route('/logout')
def logout():
	logout_user()
	flash('logged out')
	return redirect('/login')


@app.route('/favicon.ico')
def favicon():
	return send_file('static/assets/favicon.ico')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html', version=__version__)


@app.route('/createaccount', methods=['GET', 'POST'])
def hash():
	match request.method:
		case 'GET':
			return render_template('/createaccount.html')
		case 'POST':
			# return "dont accually create a account right now, it works but i can't delete them yet"
			try:
				User.query.filter_by(username=request.form['username']).first()
				flash('Account Already exists')
				return render_template('/createaccount.html')
			except:
				usr = User(username=request.form['username'],
						passhash=createPwHash(request.form['password']),
						email=request.form['email'],
						mcname=request.form['mcname'],
						uuid=request.form['uuid'])

				db.session.add(usr)
				db.session.commit()
				flash('Account Created')
				return render_template('/createaccount.html')
		


#--------
# models

@loginmng.user_loader
def user_loader(userId):
	return User.query.get(userId)


class User(db.Model, UserMixin):

	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	active = db.Column(db.Boolean, default=True)
	email = db.Column(db.String, unique=True)
	username = db.Column(db.String, unique=True)
	passhash = db.Column(db.String)
	uuid = db.Column(db.String, unique = True)
	mcname = db.Column(db.String, unique = True)
	authenticated = db.Column(db.Boolean, default = False)

	def is_active(self):
		return self.active
	
	def is_anonymous(self):
		return False # not supported but needed by flask

	def get_id(self):
		return self.id

	def get_email(self):
		return self.email
	
	def get_username(self):
		return self.username

	def get_passhash(self):
		return self.passhash
	
	def get_uuid(self):
		return self.uuid
	
	def get_mcname(self):
		return self.mcname





		

if __name__ == "__main__":
	


	app.run(debug=True,
	 		port=5000,
			host='0.0.0.0'
			)
	