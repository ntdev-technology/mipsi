from flask import Flask, render_template, send_file, request
import sqlite3
import bcrypt

def getDBConn(db: str) -> sqlite3.Connection:
	conn = sqlite3.connect(f'db/{db}.db')
	return conn
	
def createPwHash(password: str) -> str:
	salt = bcrypt.gensalt()
	hashpw = bcrypt.hashpw(password.encode('utf-8'), salt)
	shashpw = f'{salt.decode("utf-8")}|{hashpw.decode("utf-8")}'
	return shashpw

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba74a4e1a84eddcc42742bb1e0f2a80abe10ad165b010855'

@app.route('/')
def home():
	return "Hello World"

@app.route('/login', methods=['GET', 'POST'])
def login():
	match request.method:
		case 'GET':
			return render_template('login.html')
		case 'POST':
			print(request.form['username'])
			print(request.form['password'])
			return 'login succes'
		
@app.route('/favicon.ico')
def favicon():
	return send_file('static/favicon.ico')

@app.route('/createaccount', methods=['GET', 'POST'])
def hash():
	match request.method:
		case 'GET':
			return render_template('/createaccount.html', text='Your hash will appear here')
		case 'POST':
			return render_template('/createaccount.html', text=createPwHash(request.form['password'])
)

if __name__ == "__main__":
	app.run(debug=True, port=5000, host='0.0.0.0')