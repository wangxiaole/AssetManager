#all the imports
import sqlite3
from flask import Flask, request,session, g, redirect, url_for,\
	abort, render_template, flash
from contextlib import closing
#configuation
DATABASE= '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWROD = 'default'

#create our little app
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
@app.before_request
def before_request():
	g.db = connect_db()

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g,'db', None)
	if db is not None:
		db.close()

@app.route('/user/<username>')
def myAssets(username):
	session['myAssets_in'] = True
	return render_template('myAssets.html',username=username)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWROD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You ware logged in')
			return redirect(url_for('myAssets',username=request.form['username']))
	return render_template('login.html', error=error)

#control for log_out
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged_out')
	return redirect(url_for('show_entries'))


if __name__ == '__main__':
	app.run(host = '0.0.0.0')