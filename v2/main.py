from flask import Flask, flash, render_template, send_file, redirect, Response, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_security import Security, SQLAlchemySessionUserDatastore, RoleMixin, roles_accepted
from flask_sqlalchemy import SQLAlchemy
from termcolor import colored
from exceptions import RoleNotFoundError
from datetime import datetime
from typing import Callable
import subprocess
import threading
import bcrypt
import json
import ast
import os
import re


__version__ = '1.0.0-dev'
__srv_name__ = 'testsrv'
__email_pattern__ = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


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


#--------------------
# default jinja vars

@app.context_processor
def injVars():
	return dict(current_user=current_user, version=__version__, srvName=__srv_name__)


#--------------------------------
# endpoints / html build scripts


@app.route('/favicon.ico')
def favicon():
	return send_file('static/assets/favicon.ico')

@app.route('/')
def root():
	return redirect('/login')
	
@app.route('/login', methods=['GET', 'POST'])
def login() -> Callable:
	match request.method:
		case 'GET':
			if current_user.is_authenticated:
				return redirect('/dashboard')
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
					flash('Username or Password incorrect') # password
					return render_template('/login.html')	
			except Exception as e:
				print(e)
				flash('Username or Password incorrect') # user doesn't exist, username
				return render_template('/login.html')

@app.route('/createaccount', methods=['GET', 'POST'])
def hash():
	match request.method:
		case 'GET':
			return render_template('/createaccount.html')
		case 'POST':
			# return "Don't actually create a account right now, it works but i can't delete them yet" # comment out line to activate account registration
			if User.query.filter_by(username=request.form['username']).first():
				flash('Account already exists')
				return render_template('/createaccount.html')
			else:
				usr = User(username=request.form['username'],
						passhash=createPwHash(request.form['password']),
						email=request.form['email'])
				
				role = Role.query.filter_by(id=0).one()
				usr.roles.append(role)

				db.session.add(usr)
				db.session.commit()
				flash('Account Created')
				return render_template('/createaccount.html')


@app.route('/logout')
@roles_accepted('admin', 'operator', 'player')
def logout():
	if logout_user():
		flash('logged out')
		return redirect('/login')

@app.route('/dashboard')
@roles_accepted('admin', 'operator', 'player')
def dashboard():
	return render_template('dashboard.html')

@app.route('/access')
@roles_accepted('admin', 'operator', 'player')
def access():
	#flash('Account already registered')
	return render_template('access.html', version=__version__)

@app.route('/link_mc_acc', methods=['GET', 'POST'])
@roles_accepted('admin', 'operator', 'player')
def link_mc_acc():
	match request.method:
		case 'GET':
			if current_user.mcname != None:
				flash('minecraft account already linked')
				return redirect('/access')
			return render_template('/link_mc_acc.html')
		
		case 'POST':
			current_user.mcname = request.form['mcname']
			current_user.uuid = request.form['uuid']
			db.session.commit()

			flash('Minecraft Account Data Succesfull Linked')
			return redirect('/access')

	return render_template('link_mc_acc.html')

@app.route('/mcconsole')
@roles_accepted('admin', 'operator')
def console():

	return render_template('mcconsole.html')


@app.route('/files')
def files():
	
	return 'files, not make yet <a href="/dashboard">back</a>'

@app.route('/admin')
@roles_accepted('admin')
def admin():

	return render_template('admin.html')

@app.route('/users', methods=['GET', 'DELETE'])
@roles_accepted('admin')
def users():
	match request.method:
		case 'GET':
			users = User.query.all()
			return render_template('/users.html', userlist=users)
		case 'DELETE':
			try:
				id = request.headers.get('id')
				usr = User.query.filter_by(id=id).first()
				print(colored(f'USER {id}:{usr.username} DELETED', 'red'))
				flash(f'user {usr.username} deleted')
				usr.delete()
				db.session.commit()
				return {}, 200 # return 200:OK
			except:
				return {}, 404 # return 404:NOT FOUND
			
@app.route('/users/<int:userId>', methods=['GET', 'UPDATE', 'DELETE'])
@roles_accepted('admin')
def user(userId):
	match request.method:
		case 'GET':
			usrIDS = [usr.id for usr in User.query.all()]
			closest = min(usrIDS, key=lambda x:abs(x-userId))
			if userId != closest:
				return redirect(f'/users/{closest}')
			usr = User.query.filter_by(id=userId).first()
			if usr == None:
				usr = User.query.filter_by(id=0).first()

			usrjson = usr.tojson()
			return render_template('/user.html', user=usr, userJson=usrjson)
			
		case 'UPDATE':
			item = request.headers.get('item')
			val = request.headers.get(f'{item}')
			usr = User.query.filter_by(id=userId).first()

			if item == 'roles':
				rolelst = ast.literal_eval(val)		# convert a string in list format ('[1,2,3]') to a list ([1,2,3])
				val = usr.updateRoles(rolelst)
			elif item == 'id':
				setattr(usr, item, val)
				db.session.commit()
				# return redirect(f'/users/{val}')	# redirect to the new page when a users id is updated instead of stayting on a id that doesn't exist anymore
			elif item in ['username', 'email', 'mcname', 'uuid']:
				setattr(usr, item, val)
				
			db.session.commit()
			return Response(f'{{"item": "{item}", "value": "{val}"}}', status=200)

		case 'DELETE':
			raise NotImplementedError()














# @app.route('/temp')`
# def temp():
# 	usr = User(id=0)
# 	db.session.add(usr)
# 	db.session.commit()
# 	return 'hi'`

# @app.route('/add_role') # temp
# def add():
# 	role = Role.query.filter_by(id=0).first() # 0: player, 1: operator, 2: admin
# 	current_user.roles.append(role)
# 	db.session.commit()
# 	return "succes"

# @app.route('/delete') # temp
# def delete():
# 	# User.query.filter_by(username='test2').first().delete()
# 	current_user.delete()
# 	db.session.commit()
# 	flash('account deleted')
# 	return redirect('/login')


		


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
	roles = db.relationship('Role', secondary=roles_users, backref='User')

	def delete(self) -> bool:
		try:
			db.session.delete(self)
			return True
		except:
			return False

	def __repr__(self) -> str:
		return f'User instance with username:{self.username}, roles:{self.roles}' # "&lt" and "&gt" are needed to get a < and > to display in html

	def __str__(self) -> str:
		return f'User: {self.username}, Roles: {self.roles}'

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
	
	def updateRoles(self, roles):
		self.roles.clear()
		for roleId in roles:
			role = Role.query.filter_by(id=roleId).first()
			if role:
				self.roles.append(role)
			else:
				raise RoleNotFoundError()
		db.session.commit()
		return self.roles

	def tojson(self):
		user_data = {
			'id': self.id,
			'active': self.active,
			'email': self.email,
			'username': self.username,
			'uuid': self.uuid,
			'mcname': self.mcname,
			'authenticated': self.authenticated,
			'roles': [f'{role.id}:{role.name}' for role in self.roles]
		}
		return json.dumps(user_data)




class Role(db.Model, RoleMixin):
	__tablename__ = 'role'
	id   = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(10), unique=True)

	def __repr__(self):
		return f'{self.id}:{self.name}'
	
	def __str__(self):
		return f'&lt {self.id}, {self.name} &gt'


#-----------
# app logic		


usrds = SQLAlchemySessionUserDatastore(db.session, User, Role)
sec = Security(app, usrds)



if __name__ == "__main__":
	with app.app_context():	# scan db tables
		db.create_all()

	app.run(debug=True,
	 		port=5000,
			host='0.0.0.0'
			)
	