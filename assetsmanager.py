#all the imports
import sqlite3
from flask import Flask, request,session, g, redirect, url_for,\
	abort, render_template, flash
from contextlib import closing

#configuation
DATABASE= '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'

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

@app.route('/user/<userid>')
def myAssets(userid):
	if session['logged_in'] == True:
		session['myAssets_in'] = True
		sql = '''
			select  t.*, c.type, t.time as type
				from 
				(
					select asset_id, max(time) as time from use_record 
					group by asset_id
				) 
					as p
					join use_record as t
					on p.time = t.time
					join asset_info as c
					on p.asset_id = c.asset_id
					where t.employee_id = ?
			'''
		cur = g.db.execute(sql, [userid])
		entries = [dict(productID=row[2], productType=row[5], time =row[6]) for row in cur.fetchall()]
		return render_template('myAssets.html',entries=entries)
	return render_template('404.html')

@app.route('/allAssets',methods=['GET', 'POST'])
def allAssets():
	
	entries = []

	curType = g.db.execute('select DISTINCT type FROM asset_info')
	entries1 = [dict(productType=row[0]) for row in curType.fetchall()]

	curModel = g.db.execute('select DISTINCT model FROM asset_info')
	entries2 = [dict(productModel=row[0]) for row in curModel.fetchall()]

	if request.method == 'POST':
		if request.form['key'] == '0':
			sql = '''
				select asset_id from asset_info
			'''
			rv = g.db.execute(sql).fetchall()
			entries = []
			if len(rv) != 0:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,a.destination,a.model,b.employee_id 
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						where a.asset_id = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[row[0],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(productID=rowInfo[0], productType=rowInfo[1],status=rowInfo[2],destination=rowInfo[3],productModel=rowInfo[4],employee_id=rowInfo[5]))
			else:
				return render_template('allAssets.html')

		if request.form['key'] == '1':
			sql = '''
				select asset_id from asset_info where model = ?
			'''
			rv = g.db.execute(sql,[request.form['model']]).fetchall()
			entries = []
			if len(rv) != 0:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,a.destination,a.model,b.employee_id 
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						where a.model = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[request.form['model'],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(productID=rowInfo[0], productType=rowInfo[1],status=rowInfo[2],destination=rowInfo[3],productModel=rowInfo[4],employee_id=rowInfo[5]))
			else:
				return render_template('allAssets.html')
		
		if request.form['key'] == '2':

			sql = '''
				select asset_id from asset_info where type = ?
			'''
			rv = g.db.execute(sql,[request.form['AllSetstype']]).fetchall()
			entries = []
			if len(rv) != 0:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,a.destination,a.model,b.employee_id 
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						where a.type = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[request.form['AllSetstype'],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(productID=rowInfo[0], productType=rowInfo[1],status=rowInfo[2],destination=rowInfo[3],productModel=rowInfo[4],employee_id=rowInfo[5]))
			
		if request.form['key'] == '3':
			sql = '''
				select asset_id from asset_info where state = ?
 			'''
			rv = g.db.execute(sql,[request.form['status']]).fetchall()
			entries = []
			if len(rv) != 0:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,a.destination,a.model,b.employee_id 
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						where a.state = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[request.form['status'],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(productID=rowInfo[0], productType=rowInfo[1],status=rowInfo[2],destination=rowInfo[3],productModel=rowInfo[4],employee_id=rowInfo[5]))

	return render_template('allAssets.html',entries = entries,entries1 = entries1,entries2 = entries2)
# @app.route('/addAsset')
# def addAsset():
# 	return render_template('addAsset.html')

@app.route('/passwordChange')
def passwordChange():
	return render_template('passwordChange.html')
	
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		cur = g.db.execute('select * from employee_info where employee_id = ?',
				[request.form['userid']])
		# cur = g.db.execute('select * from personnelInformation where name = ?',[request.form['username']])
		if (cur.fetchone() is None):
			error = 'Invalid username'
			return render_template('login.html', error=error)
		cur = g.db.execute('select * from employee_info where employee_id = ? and password = ?',
				[request.form['userid'],request.form['password']])
		userInfo=[dict(userid = row[0],password = row[2],level = row[8]) for row in cur.fetchall()]
		if len(userInfo) == False:
			error = 'Invalid password'
			return render_template('login.html', error=error)		
		session['logged_in'] = True
		session['userid'] = userInfo[0]['userid']
		session['password'] = userInfo[0]['password']
		session['level'] = userInfo[0]['level']
		flash('You ware logged in')
		return redirect(url_for('myAssets',userid=request.form['userid']))
	return render_template('login.html')

#control for log_out
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('myAssets_in',None)
	session.pop('userid',None)
	session.pop('password',None)
	session.pop('level',None)
	flash('You were logged_out')
	return redirect(url_for('login'))


@app.route('/passwordChangeError', methods=['GET', 'POST'])
def change_personel_information():
	error = None
	oldpassword = request.form['oldpassword']
	newpassword = request.form['newpassword']
	confirm = request.form['confirm']

	if not session.get("logged_in"):
		return render_template('login.html')
	if request.method == 'POST':
		if oldpassword != session['password']:
			error = 'Old password  incorrect!'
		elif newpassword != confirm:
			error = 'Passwords can not match!'
		else:
			sql = '''
                update employee_info set password = ? where employee_id = ?  
            '''
			g.db.execute(sql, [newpassword, session['userid']])
			g.db.commit()
			return redirect(url_for('myAssets',userid = session['userid']))
	return render_template('passwordChange.html', error=error)

@app.route('/addAsset',methods=['GET','POST'])
def addAsset():
	curType = g.db.execute('select DISTINCT type FROM asset_info')
	entries1 = [dict(productType=row[0]) for row in curType.fetchall()]

	curModel = g.db.execute('select DISTINCT model from asset_info')
	entries2 = [dict(productModel=row[0]) for row in curModel.fetchall()]
	
	if request.method == 'POST':
		cur = g.db.execute('select * from asset_info where asset_id = ?',[request.form['assetId']])
		rv = cur.fetchall()
		if len(rv) == 0:
			g.db.execute('insert into asset_info (asset_id,model,type,state,destination,fromdpt,comment) values (?,?,?,?,?,?,?)',
			[request.form['assetId'],request.form['model'],request.form['assetType'],request.form['state'],request.form['destination'],request.form['fromDpt'],request.form['comment']])
			sql = '''
				insert into use_record(employee_id,asset_id,time,comment) values(?,?,datetime('now', 'localtime'),?)
			'''

			g.db.execute(sql,[request.form['employeeId'],request.form['assetId'],request.form['comment']])
			g.db.commit()
		else:
			g.db.execute('update asset_info set model = ?,type = ?,state= ?,destination= ?,fromdpt = ?,comment= ? where asset_id= ?',[request.form['model'],request.form['assetType'],request.form['state'],request.form['destination'],request.form['fromDpt'],request.form['comment'],request.form['assetId']])
			g.db.execute('update use_record set employee_id = ?,time = ?,comment = ? where asset_id = ?',
			[request.form['employeeId'],datetime('now', 'localtime'),request.form['comment'],request.form['assetId']])
			g.db.commit()
	return render_template('addAsset.html',entries1 = entries1,entries2 = entries2)

@app.route('/modifyAssetInfo',methods=['GET','POST'])
def modifyAssetInfo():

	cur = g.db.execute('select DISTINCT type from asset_info')
	assetType = [dict(productType=row[0]) for row in cur.fetchall()]

	curModel = g.db.execute('select DISTINCT model from asset_info')
	assetModel = [dict(productModel=row[0]) for row in curModel.fetchall()]

	if request.method == 'POST':
		asset_id = request.form['assetId']
		asset_model = request.form['model']
		asset_type = request.form['type']
		user_id = request.form['username']
		destination = request.form['destination']
		asset_status = request.form['status']
		#change asset type or state
		sql = '''
            select model,type,state,destination from asset_info where asset_id = ?
    	'''
		curInfo = g.db.execute(sql,[asset_id])
		asset_info = [dict(asset_model = row[0],asset_type = row[1],asset_status = row[2],destination = row[3]) for row in curInfo]
		if asset_model != asset_info[0]['asset_model'] or asset_type != asset_info[0]['asset_type'] or asset_status != asset_info[0]['asset_status'] or destination != asset_info[0]['destination']:
			sql = '''
            	update asset_info set model = ?,type = ?,state = ?,destination = ? where asset_id = ?
    		'''
			g.db.execute(sql,[asset_model,asset_type,asset_status,destination,asset_id])
			g.db.commit()
		#change employee id(update tabel use_record)
		sql = '''
			select employee_id from use_record where asset_id = ? and time = (select max(time) from use_record where asset_id = ?)
		'''
		curId = g.db.execute(sql,[asset_id,asset_id])
		employee_id = [dict(employee_id = row[0]) for row in curId]
		if user_id != employee_id[0]['employee_id']:
			sql = '''
            	insert into use_record(employee_id,asset_id,time,comment) values(?,?,datetime('now', 'localtime'),"")
    		'''
			g.db.execute(sql,[user_id,asset_id])
			g.db.commit()
		return redirect(url_for('allAssets'))
	return render_template('modifyAssetInfo.html',entries = assetType,entries1 = assetModel)

@app.route('/assetSearch',methods=['GET','POST'])
def assetSearchDisplay():
	curType = g.db.execute('select distinct type from asset_info')
	assetType = [dict(productType=row[0]) for row in curType.fetchall()]

	curModel = g.db.execute('select DISTINCT model from asset_info')
	assetModel = [dict(productModel=row[0]) for row in curModel.fetchall()]
	
	cur = None
	error = None
	if request.method == 'POST':
		#select by asset_id	
		if request.form['key'] == '1': 
			sql = '''
				select a.asset_id,a.type,a.state,c.employee_id,c.name,c.email,c.tel,c.jabber,a.model 
				from asset_info as a 
				join use_record as b 
				on a.asset_id = b.asset_id 
				join employee_info as c 
				on b.employee_id = c.employee_id 
				where a.asset_id = ? and b.time = (select max(time) from use_record where asset_id = ?)
			'''
			cur = g.db.execute(sql,[request.form['asset_id'],request.form['asset_id']])
			rv = cur.fetchall()
			if len(rv) == 0:
				error = 'No this productID!'
				return render_template('assetSearch.html',error = error)
			else:
				entries = [dict(asset_id=row[0], asset_type=row[1], asset_status=row[2], employee_id=row[3], employee_name=row[4], employee_email=row[5], employee_tel=row[6], employee_jabber=row[7], asset_model=row[8]) for row in rv]	
				return render_template('assetSearch.html',entries = entries,assetType = assetType,assetModel = assetModel)
		#select by model
		elif request.form['key'] == '2':
			entries = []
			sql = '''
				select * from asset_info where model = ?
    		'''
			cur = g.db.execute(sql, [request.form['model']])
			rv = cur.fetchall()
			if len(rv) == 0:
				error = 'No this productModel!'
				return render_template('assetSearch.html',error = error)
			else:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,c.employee_id,c.name,c.email,c.tel,c.jabber,a.model 
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						join employee_info as c 
						on b.employee_id = c.employee_id 
						where a.model = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[request.form['model'],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(asset_id=rowInfo[0], asset_type=rowInfo[1], asset_status=rowInfo[2], employee_id=rowInfo[3], employee_name=rowInfo[4], employee_email=rowInfo[5], employee_tel=rowInfo[6], employee_jabber=rowInfo[7], asset_model=rowInfo[8]))
				return render_template('assetSearch.html',entries = entries,assetType = assetType,assetModel = assetModel)
		#select by type
		elif request.form['key'] == '3':
			entries = []
			sql = '''
				select * from asset_info where type = ?
    		'''
			cur = g.db.execute(sql, [request.form['asset_type']])
			rv = cur.fetchall()
			if len(rv) == 0:
				error = 'No this productType!'
				return render_template('assetSearch.html',error = error)
			else:
				for row in rv:
					sql = '''
						select a.asset_id,a.type,a.state,c.employee_id,c.name,c.email,c.tel,c.jabber,a.model
						from asset_info as a 
						join use_record as b 
						on a.asset_id = b.asset_id 
						join employee_info as c 
						on b.employee_id = c.employee_id 
						where a.type = ? and b.time = (select max(time) from use_record where asset_id = ?)
					'''
					curInfo = g.db.execute(sql,[request.form['asset_type'],row[0]])
					rowInfo = curInfo.fetchone()
					if rowInfo is not None:
						entries.append(dict(asset_id=rowInfo[0], asset_type=rowInfo[1], asset_status=rowInfo[2], employee_id=rowInfo[3], employee_name=rowInfo[4], employee_email=rowInfo[5], employee_tel=rowInfo[6], employee_jabber=rowInfo[7], asset_model=rowInfo[8]))
				return render_template('assetSearch.html',entries = entries,assetType = assetType,assetModel = assetModel)
		#select by state
		elif request.form['key'] == '4':
			entries = []

			sql = '''
				select * from asset_info where state = ?
    		'''
			cur = g.db.execute(sql, [request.form['status']])
			rv = cur.fetchall()
			if len(rv) == 0:
				error = 'No this asset status!'
				return render_template('assetSearch.html',error = error)
			else:
				if request.form['status'].encode("gbk")!='\xcf\xfa\xbb\xd9':
					
					for row in rv:
						sql = '''
							select a.asset_id,a.type,a.state,c.employee_id,c.name,c.email,c.tel,c.jabber,a.model 
							from asset_info as a 
							join use_record as b 
							on a.asset_id = b.asset_id 
							join employee_info as c 
							on b.employee_id = c.employee_id 
							where a.state = ? and b.time = (select max(time) from use_record where asset_id = ?)
						'''
						curInfo = g.db.execute(sql,[request.form['status'],row[0]])
						rowInfo = curInfo.fetchone()
						if rowInfo is not None:
							entries.append(dict(asset_id=rowInfo[0], asset_type=rowInfo[1], asset_status=rowInfo[2], employee_id=rowInfo[3], employee_name=rowInfo[4], employee_email=rowInfo[5], employee_tel=rowInfo[6], employee_jabber=rowInfo[7], asset_model=rowInfo[8]))
					return render_template('assetSearch.html',entries = entries,assetType = assetType,assetModel = assetModel)
				else:
					#raise
					for row in rv:
						sql = '''
							select a.asset_id,a.type,a.state,a.model from asset_info as a where a.state = ?
						'''
						curInfo = g.db.execute(sql,[request.form['status']])
						rowInfo = curInfo.fetchone()
						if rowInfo is not None:
							entries.append(dict(asset_id=rowInfo[0], asset_type=rowInfo[1], asset_status=rowInfo[2], employee_id="", employee_name="", employee_email="", employee_tel="", employee_jabber="", asset_model=rowInfo[3]))
					return render_template('assetSearch.html',entries = entries,assetType = assetType,assetModel = assetModel)
	return render_template('assetSearch.html',assetType = assetType,assetModel = assetModel)

@app.route('/assetUsingHistory/<asset_id>',methods=['GET','POST'])
def assetUsingHistory(asset_id):	
	sql = '''
			select a.email,a.name,b.time,a.tel,a.dept from use_record as b
			join employee_info as a
			on a.employee_id = b.employee_id
			where b.asset_id = ?
			'''
	cur = g.db.execute(sql,[asset_id])
	entries = [dict(email=row[0],name=row[1],time=row[2],tel=row[3],dept=row[4]) for row in cur.fetchall()]
	return render_template('assetUsingHistory.html',entries = entries)

@app.route('/updateEmployeeInfomation',methods=['GET','POST'])
def updateEmployeeInfomation():
	sql = '''
		select name,dept,"group",tel,jabber,email from employee_info where employee_id = ?
	'''
	cur = g.db.execute(sql,[session['userid']])
	employeeInfo = cur.fetchone()
	entry = [dict(name=employeeInfo[0],dept=employeeInfo[1],group=employeeInfo[2],tel=employeeInfo[3],jabber=employeeInfo[4],email=employeeInfo[5])]
	if request.method == 'POST':
		employee_name = request.form['employee_name']
		dept = request.form['dept']
		group = request.form['group']
		tel = request.form['tel']
		jabber = request.form['jabber']
		email = request.form['email']
		entry = [dict(name=employee_name,dept=dept,group=group,tel=tel,jabber=jabber,email=email)]
		sql = '''
			update employee_info set name = ?,dept = ?,"group" = ?,tel = ?,jabber = ?,email = ? where employee_id = ?
		'''
		g.db.execute(sql,[employee_name,dept,group,tel,jabber,email,session['userid']])
		g.db.commit()

		return render_template('updateEmployeeInfo.html',entry=entry)
	return render_template('updateEmployeeInfo.html',entry=entry)

if __name__ == '__main__':
	app.run(host = '0.0.0.0')