from flask import Flask, flash, render_template, send_file, redirect, request
from flask_login import LoginManager, login_manager, UserMixin, login_user, logout_user
from flask_security import Security, SQLAlchemySessionUserDatastore, RoleMixin, roles_accepted
from flask_sqlalchemy import SQLAlchemy
from termcolor import colored
from datetime import datetime
from typing import Callable
import subprocess
import threading
import random
import bcrypt
import os
import re


__version__ = '1.0.0'

	
def createPwHash(password: str) -> str:
	salt = bcrypt.gensalt()
	hashpw = bcrypt.hashpw(password.encode('utf-8'), salt)
	return f'{salt.decode("utf-8")}|{hashpw.decode("utf-8")}'
	

def checkPw(dbpw: str, ippw: str) -> bool:
	salt, hash = dbpw.split('|')
	pwhash = bcrypt.hashpw(ippw.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
	if hash == pwhash:
		return True
	else:
		return False


#------------
# app init's

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba74a4e1a84eddcc42742bb1e0f2a80abe10ad165b010855'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(os.getcwd()+"/db/users.db")}'
db = SQLAlchemy()
db.init_app(app)
loginmng = LoginManager()
loginmng.init_app(app)



#--------------------------------
# endpoints / html build scripts

@app.route('/')
def home() -> Callable:
	return redirect('/login') # Returns main site to the login window.



@app.route('/login', methods=['GET', 'POST'])
def login() -> Callable:
	match request.method:
		case 'GET':
			return render_template('login.html')
		case 'POST':
			try:
				usr: User = User.query.filter_by(
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
				flash('Username Invalid') # user doesn't exist
				return render_template('/login.html')

		

@app.route('/logout')
def logout():
	logout_user()
	flash('logged out')
	return redirect('/login')


@app.route('/favicon.ico')
def favicon():
	return send_file('static/assets/favicon.ico')


@app.route('/dashboard')
# @roles_accepted('Admin')
def dashboard():
	
	return render_template('dashboard.html', version=__version__, username='testusr')

@app.route('/access', methods=['GET', 'POST'])
def access():
	
	return render_template('access.html')


@app.route('/createaccount', methods=['GET', 'POST'])
def hash():
	match request.method:
		case 'GET':
			return render_template('/createaccount.html')
		case 'POST':
			# return "Don't actually create a account right now, it works but i can't delete them yet" # comment out line to activate account registration
			try:
				User.query.filter_by(username=request.form['username']).first()
				flash('Account already exists')
				return render_template('/createaccount.html')
			except:
				usr = User(username=request.form['username'],
						passhash=createPwHash(request.form['password']),
						email=request.form['email'])

				db.session.add(usr)
				db.session.commit()
				flash('Account Created')
				return render_template('/createaccount.html')
		


#--------
# models

@loginmng.user_loader
def user_loader(userId):
	return User.query.get(userId)

roles_users = db.Table('roles_users',
		       		   db.Column('userId', db.Integer, db.ForeignKey('user.id')),
					   db.Column('roleId', db.Integer, db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
	
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	active = db.Column(db.Boolean, default=True)
	email = db.Column(db.String, unique=True)
	username = db.Column(db.String, unique=True)
	passhash = db.Column(db.String)
	uuid = db.Column(db.String, unique = True)
	mcname = db.Column(db.String, unique = True)
	authenticated = db.Column(db.Boolean, default = False)
	roles = db.relationship('Role', secondary=roles_users, backref='roled')

	def is_active(self) -> str:
		return self.active
	
	def is_anonymous(self) -> str:
		return False # not supported but needed by flask

	def get_id(self) -> str:
		return self.id

	def get_email(self) -> str:
		return self.email
	
	def get_username(self) -> str:
		return self.username

	def get_passhash(self) -> str:
		return self.passhash
	
	def get_uuid(self) -> str:
		return self.uuid
	
	def get_mcname(self) -> str:
		return self.mcname

class Role(db.Model, RoleMixin):
	__tablename__ = 'role'
	id   = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(10), unique=True)


#-----------
# app logic		


# usrds = SQLAlchemySessionUserDatastore(db.session, User, Role)
# sec = Security(app, usrds)



if __name__ == "__main__":
	with app.app_context():	# scan db tables
		db.create_all()

	app.run(debug=True,
	 		port=5000,
			host='0.0.0.0'
			)
	