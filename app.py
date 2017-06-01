from flask import Flask,render_template,redirect,request,make_response,redirect,url_for,jsonify
from pymongo import MongoClient
from argon2 import PasswordHasher
import json
from bcrypt import hashpw,gensalt
#to query collections by their Id
from bson.objectid import ObjectId
from time import gmtime, strftime
import string 
import random
from time import gmtime,strftime
from flask_uploads import UploadSet, configure_uploads, IMAGES
from datetime import *
import datetime
from bson.json_util import dumps


#Connecting to DB

client = MongoClient(connect=False)
db = client.neem_tree




# id_generator
def key_gen(size=10, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

ph = PasswordHasher()

app = Flask(__name__)



#Configuring where photos should be uploaded.
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img/'
configure_uploads(app, photos)


#Login for Unit Holder and Neem Tree Staff
@app.route("/")
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
	user = 0
	unit = 0
	if request.method == 'POST':
		#Verify login form data

#The way the login works is it checks if the email exists in either unit holder or neem tree staff
#If it's in either it logs in, and inserts a hashed key in the 'active' users DB, the same key is in your cookies,
#This makes sure it's you logging in and on one device only.

		user = db.staff.find({'email': request.json['email']}).count()
		unit = db.unit_holder.find({'email': request.json['email']}).count()
        if user  == 1 and unit == 0:
			
			user = db.staff.find_one({'email': request.json['email']})
			try:
				if ph.verify(user['password'],request.json['password']) == True:

					key = key_gen()
					hashed_key = hashpw(key,gensalt())
					active_user = {
	                    'email' : request.json['email'],
                    	'key'  : hashed_key,
                    	'type'  : 'staff'
                	}
				
					response = {
					"response": "success",
					"email":request.json['email'],
					"key": hashed_key,
					"type":"staff"
					}
					

					db.active.insert_one(active_user)
					response = json.dumps(response)
					
					return response


			except:
				response = {
					"response": "failure",
					"info"  :  "Email or Password is incorrect"
					}
				response = json.dumps(response)
				return response
				
			
				


        if unit == 1 and user == 0:
			
			user = db.unit_holder.find_one({'email': request.json['email']})
			try:
				if ph.verify(user['password'],request.json['password']) == True:

					key = key_gen()
					hashed_key = hashpw(key,gensalt())
					active_user = {
	                    'email' : request.json['email'],
                    	'key'  : hashed_key,
                    	'type'  : 'unit'
                	}
					response = {
					"response": "success",
					"email":request.json['email'],
					"key": hashed_key,
					"type":"unit"
					}
					db.active.insert_one(active_user)
					response = json.dumps(response)
					return response
		
			except:
				response = {
					"response": "failure",
					"info"  :  "Email or Password is incorrect"
					}
				response = json.dumps(response)
				return response
		
        if user and unit == 0:
			response = {
				"response": "failure",
				"info"  :  "Email or Password is incorrect"
				}
			response = json.dumps(response)
			return response
	return render_template('login.html')



#Add user 
@app.route("/add")
def add():
	return render_template('add_user.html')

#Neem Tree Staff Homepage
@app.route('/home/staff')
def home_staff():
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff' :
		to_approve = db.approve_intern.find({}).count()
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email':user['email']})
		return render_template('home_staff.html',user=user,approve=to_approve)
	else:
		return redirect('/login')

#Unit Holder Homepage
@app.route('/home/unit')
def home_unit():
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'unit':
		user = db.active.find_one({'key' : key})
		user = db.unit_holder.find_one({'email':user['email']})
		return render_template('home_unit.html',user=user)

	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff' :
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email':user['email']})
		return redirect('/home/staff')



#Create Neem Tree Staff API
@app.route("/add_staff", methods=['POST'])
def add_staff():
	unit = db.unit_holder.find({'email':request.json['email']}).count()
	approve_unit = db.unit_holder.find({'email':request.json['email']}).count()
	user = db.staff.find({'email':request.json['email']}).count()
	approve_user = db.approve_staff.find({'email':request.json['email']}).count()
	user = unit+approve_unit+user+approve_user

	if user != 0:
		response = {}
		response['response'] = "exists"
		response = json.dumps(response)
		return response
	else:
		data ={
		"name":request.json['name'],
		"password": ph.hash(request.json['password']),
		"email":request.json['email'],
		"phone_number":request.json['phone_number']
		}

		try:
			db.approve_staff.insert_one(data)
			response = {}
			response['response'] = "success"
			response = json.dumps(response)
			return response
		except:
			response = {}
			response['response'] = "failure"
			response = json.dumps(response)
			return response



#Create Unit Holder Account API
@app.route("/add_unit_holder", methods=['POST'])
def add_unit_holder():
	unit = db.unit_holder.find({'email':request.json['email']}).count()
	approve_unit = db.unit_holder.find({'email':request.json['email']}).count()
	user = db.staff.find({'email':request.json['email']}).count()
	approve_user = db.approve_staff.find({'email':request.json['email']}).count()
	user = unit+approve_unit+user+approve_user

	if user != 0:
		response = {}
		response['response'] = "exists"
		response = json.dumps(response)
		return response

	else:
		data ={
		"unit_name":request.json['unit_name'],
		"password": ph.hash(request.json['password']),
		"name":request.json['person_name'],
		"email":request.json['email'],
		"phone_number":request.json['phone_number'],
		}
		try:
			db.approve_unit_holder.insert_one(data)
			response = {}
			response['response'] = "success"
			response = json.dumps(response)
			return response
		except:
			response = {}
			response['response'] = "failure"
			response = json.dumps(response)
			return response


@app.route('/add/intern', methods=['GET','POST'])
def add_an_intern():
	callback = ''
	key = request.cookies.get('key')
	error = ''
	usr = db.active.find_one({'key' : key})


	if db.active.find({'key' : key}).count() != 0:

		user = db.active.find_one({'key' : key})
		if db.staff.find({'email':user['email']}).count() != 0:
			return redirect('/add/intern/staff')
		
		elif db.unit_holder.find({'email':user['email']}).count() != 0 and usr['type'] == 'unit':
			user = db.unit_holder.find_one({'email':user['email']})
			

			if request.method == 'POST':
				if len(request.form['email']) == 0:
					error = 'Invalid email'

				if len(request.form['name'])  == 0:
					error = 'Invalid Name'

				
				if request.form['phone_number'].isdigit() != True or len(str(request.form['phone_number'])) != 10 :
					error = 'Invalid phone number'

				if error == '':

	

					start_date = request.form['start_date']
					start_month = start_date[0:3]
					start_day = start_date[3:6]
					start_year = start_date[6:10]
					start_date= start_day+start_month+start_year

					end_date = request.form['end_date']
					end_month = end_date[0:3]
					end_day = end_date[3:6]
					end_year = end_date[6:10]
					end_date= start_day+start_month+start_year



					email = request.cookies.get('email')
					user = db.unit_holder.find_one({'email'  : email })

					data = {
					"name":request.form['name'],
					"unit_name":user['unit_name'],
					"email":request.form['email'],
					"phone_number":request.form['phone_number'],
					"start_date":start_date,
					"end_date":end_date,
					"balance": 0,
					"img": photos.save(request.files['img']),
					"scheme":[],
					"created_by":user['name']
					}
					
					try:
						db.approve_intern.insert_one(data)
						callback = 'success'
						
					except:
						return "Couldn't create intern. Contact admin"

		return render_template('add_intern.html',user=user,error=error,callback=callback)
	else:
		return redirect('/login')



@app.route('/add/intern/staff', methods=['GET','POST'])
def add_intern_staff():

	key = request.cookies.get('key')
	error = ''
	user_type = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		user = db.active.find_one({'key' : key})
		if db.staff.find({'email':user['email']}).count() != 0:
			user = db.staff.find_one({'email':user['email']})

		elif db.unit_holder.find({'email':user['email']}).count() != 0:
			return redirect('/add/intern')

		else:
			return redirect('/login')

		if request.method == 'POST':

			#return filename

			if len(request.form['email']) == 0:
						error = 'Invalid email'

			if len(request.form['name'])  == 0:
						error = 'Invalid Name'

				
			if request.form['phone_number'].isdigit() != True or len(str(request.form['phone_number'])) != 10 :
            			error = 'Invalid phone number'
         	
			if error == '':
				

				start_date = request.form['start_date']
				start_month = start_date[0:3]
				start_day = start_date[3:6]
				start_year = start_date[6:10]
				start_date= start_day+start_month+start_year
				

				end_date = request.form['end_date']
				end_month = end_date[0:3]
				end_day = end_date[3:6]
				end_year = end_date[6:10]
				end_date= start_day+start_month+start_year


				email = request.cookies.get('email')
				user = db.staff.find_one({'email'  : email })
				data = {
				"name":request.form['name'],
				"unit_name":request.form['unit_name'],
				"email":request.form['email'],
				"phone_number":request.form['phone_number'],
				"start_date":start_date,
				"end_date":end_date,
				"balance": 0,
				"img": photos.save(request.files['img']),
				"scheme":[],
				"created_by":user['name']
				}
				
			
				db.intern.insert_one(data)

				#Logging
				log_data = {
				"intern_name": data['name'],
				"type": "created_intern",
				"done_by": user['name'],
				"date":strftime("%a, %d %b %Y", gmtime())
				}
				db.log.insert_one(log_data)
				return redirect('/interns')			
			
		return render_template('add_intern_staff.html',user=user,error=error)
	else:
		return redirect('/login')


@app.route('/add_scheme/<id>', methods=['GET','POST'])
def add_scheme(id):
	key = request.cookies.get('key')
	email = request.cookies.get('email')
	error = None
	callback = ''
	log_data = {}
	log = {}
	logdata = {}

	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		if db.unit_holder.find({'email': user['email']}).count() != 0:
			return redirect('/home/unit')
		else:
			user = db.intern.find_one({'_id': ObjectId(id)})
			active_user = db.staff.find_one({'email':email})

		if request.method == 'POST':
			if request.form['start_date'] and request.form['end_date'] != None:
				start_date = request.form['start_date']
				start_month = start_date[0:3]
				start_day = start_date[3:6]
				start_year = start_date[6:10]
				start_date= start_day+start_month+start_year

				end_date = request.form['end_date']
				end_year = end_date[6:10]
				end_month = end_date[0:3]
				end_day = end_date[3:6]
				end_date= end_day+end_month+end_year

		
				def apply_scheme(type_of_scheme,intern_email,doneby,end_date,start_date):
					
					data = {
					'type' : type_of_scheme,
					'start_date' : start_date,
					'end_date' : end_date
					}
					
					intern = db.intern.find_one({'email':intern_email})
					print intern['name']
					intern['scheme'].append(data)
					db.intern.save(intern)

					log = {
					"intern_name": intern['name'],
					"type": type_of_scheme,
					"done_by": doneby,
					"date":strftime("%a, %d %b %Y", gmtime())
					}
					
					db.log.insert_one(log)



				if request.form['type'] == 'Snack':
					apply_scheme('snack',user['email'],active_user['name'],end_date,start_date)
				else:
					snack = False

				if request.form['type'] == 'Breakfast':
					apply_scheme('breakfast',user['email'],active_user['name'],end_date,start_date)
				else:
					breakfast = False


				if request.form['type'] == 'Lunch':
					apply_scheme('lunch',user['email'],active_user['name'],end_date,start_date)
				else:
					lunch = False

				if request.form['type'] == 'Dinner':
					apply_scheme('dinner',user['email'],active_user['name'],end_date,start_date)
				else:
					dinner = False

				if request.form['type'] != 'None':
					callback = 'Added scheme successfully!'
				else:
					error = 'Please select a type of scheme'
			else:
				error = 'Start Date or End Date is empty!'


			
		return render_template('add_scheme.html', active_user=active_user,user=user,callback=callback,error=error)


@app.route('/remove/scheme', methods=['GET','POST'])
def remove_scheme():
	intern = db.intern.find_one({'name' : request.json['intern_name']})
	type = request.json['type']
	print type
	for i in intern['scheme']:
		if i['type'] == type:
			index = intern['scheme'].index(i)
			intern['scheme'].pop(index)
			db.intern.save(intern)
	response = {}
	response['id'] = '%s'%(intern['_id'])
	response = json.dumps(response)
	return response

#Intern List 
@app.route('/interns')
def intern_list_staff():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:

		user = db.active.find_one({'key' : key})
		if db.unit_holder.find({'email': user['email']}).count() != 0:
			user = db.unit_holder.find_one({'email':user['email']})
			interns = []
			for i in db.intern.find({'unit_name'  : user['unit_name']}):
				interns.append([[i['name']],i['email'],i['unit_name'],i['balance'],i['phone_number'],i['img'],i['_id']])
		else:
			user = db.staff.find_one({'email':user['email']})
			interns = []
			for i in db.intern.find():
				interns.append([[i['name']],i['email'],i['unit_name'],i['balance'],i['phone_number'],i['img'],i['_id']])


			 
		return render_template('interns.html',user=user,interns=interns)
	else:
		return redirect('/login')


#Individual Intern
@app.route('/intern/<id>')
def individual_intern(id):
	key = request.cookies.get('key')
	type = request.cookies.get('type')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		intern = db.intern.find_one({'_id': ObjectId(id)})
		usr_type = request.cookies.get('type')
		user = None
		if usr_type == 'staff':
			user = db.staff.find_one({'email'  :  request.cookies.get('email')})
		if usr_type == 'unit':
			if db.unit_holder.find({'email' : request.cookies.get('email')}).count() == 1:
				user = db.unit_holder.find_one({'email'  :  request.cookies.get('email')})
				if user['unit_name'] == intern['unit_name']:
					pass
				else:
					return redirect('/home/unit')

		return render_template('intern_page.html',user=user,intern=intern,type=type)
	else:
		return redirect('/login')



#Edit Intern API
@app.route("/interns/edit", methods=['GET'])
def edit_intern():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key'  :  key}).count() != 0:
		user = db.active.find_one({'key'  :  key})
		type = request.cookies.get('type')
		if type == 'staff':
			user = db.staff.find_one({'email':user['email']})
			interns = []
			for i in db.intern.find():
				interns.append([[i['name']],i['email'],i['unit_name'],i['balance'],i['phone_number'],i['img'],i['_id']])

		if type == 'unit':
			user = db.unit_holder.find_one({'email':user['email']})
			interns = []
			for i in db.intern.find({'unit_name'  : user['unit_name']}):
				interns.append([[i['name']],i['email'],i['unit_name'],i['balance'],i['phone_number'],i['img'],i['_id']])
		return render_template('edit_intern.html', user=user,interns=interns)


#Remove Intern API
@app.route("/<id>/edit", methods=['GET','POST'])
def commit_edit_intern(id):
	key = request.cookies.get('key')
	error = None
	email = request.cookies.get('email')
	if db.active.find({'key'  :  key}).count() != 0:
		

		user = db.active.find_one({'key'  :  key})
		type = request.cookies.get('type')


		#Checking if user has right to edit intern
		if type == 'staff':
			user_current = db.staff.find_one({'email'  :  user['email']})
			intern = db.intern.find_one({'_id' : ObjectId(id)})
		if type == 'unit':
			user_current = db.unit_holder.find_one({'email'  :  user['email']})
			intern = db.intern.find_one({'_id' : ObjectId(id)})
			if user['unit_name'] != intern['unit_name']:
				return redirect('/home/unit')

		if request.method == 'POST':
			name = None
			start_date = None
			end_date = None
			email = None
			phone_number = None
			
			try:
				name = request.json['name']
			except KeyError:
				pass
				
			try:
				start_date = request.json['start_date']
				start_year = start_date[0:4]
				start_month = start_date[5:7]
				start_day = start_date[8:10]
				start_date= start_day+'/'+start_month+'/'+start_year
			except KeyError:
				pass

			try:
				end_date = request.json['end_date']
				end_date = request.form['end_date']
				end_year = end_date[0:4]
				end_month = end_date[5:7]
				end_day = end_date[8:10]
				end_date= end_day+'/'+end_month+'/'+end_year
			except KeyError:
				pass
				
			try:
				email = request.json['email']
			except KeyError:
				pass
				
			try:
				phone_number = request.json['phone_number']
			except KeyError:
				pass
			
			updates = {}
			user = db.intern.find_one({'_id'  :ObjectId(id)})
			if name != None:
				transactions = db.transactions.find({'intern_name': user['name']})
				user['name'] = name
				for i in transactions:
					i['intern_name'] = name
					db.transactions.save(i)

			if start_date != None:
				user['start_date'] = start_date
			if end_date != None:
				user['end_date'] = end_date
			if email != None:
				user['email'] = email
			if phone_number != None:
				user['phone_number'] = phone_number
			db.intern.save(user)


			log_data = {
			"intern_name": intern['name'],
			"type": "edit",
			"done_by": user_current['name'],
			"date":strftime("%a, %d %b %Y", gmtime())
			}

			db.log.insert_one(log_data)
			return jsonify({'response'  : 'success'})



		return render_template('edit_individual.html',user=user_current,intern=intern,type=type)
	

	else:
		return redirect('/login')
		
@app.route('/interns/delete', methods=['GET','POST'])
def delete_intern():
	intern = db.intern.find_one({'_id':ObjectId(request.json['id'])})
	log_data = {
	"intern_name":intern['name'],
	"type":"delete",
	"done_by":request.json['done_by'],
	"date":strftime("%a, %d %b %Y", gmtime())
	}
	db.intern.delete_one({'_id':intern['_id']})
	db.log.insert_one(log_data)
	response = {}
	response['response'] = 'success'
	response = json.dumps(response)
	return response


#View Transactions
@app.route('/view_transactions', methods=['GET','POST'])
def view_transactions():
	key = request.cookies.get('key')
	error = None
	results = []
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email'  : user['email']})
		transactions = db.transactions.find().sort([('_id', -1)])

		if request.method == 'POST':

		

			if request.json['type'] == 'money_out':
				transactions = db.transactions.find({'type'  :  'money_out'}).sort([('_id', -1)])
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response


			if request.json['type'] == 'money_in':
				transactions = db.transactions.find({'type'  :  'money_in'}).sort([('_id', -1)])
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response


			if request.json['type'] == 'lowest_amount':
				transactions = db.transactions.find().sort([('amount', +1)])
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response


			if request.json['type'] == 'highest_amount':
				transactions = db.transactions.find().sort([('amount', -1)])
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response

			if request.json['type'] == 'today':
				transactions = db.transactions.find({'date':strftime("%a, %d %b %Y", gmtime())})
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response

			if request.json['type'] == 'this_month':
				transactions = db.transactions.find({'date':strftime("%a, %d %b %Y", gmtime())})
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response

			if request.json['type'] == 'this_quarter':
				transactions = db.transactions.find({'date':strftime("%a, %d %b %Y", gmtime())})
				for i in transactions:
					results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
				response = {}
				response['response'] = results
				response = json.dumps(response)
				return response




		return render_template('view_transactions.html',user=user,transactions=transactions)
	
	else:
		return redirect('/login')



#Search Transactions.
@app.route('/search/transactions', methods=['POST','GET'])
def search_transaction():
	query = request.json['query']
	results = []
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		if request.method == 'POST' and request.json['type'] == 'intern':
			transactions = db.transactions.find({'intern_name' :{'$regex' : query} }).sort([('_id', -1)])
			for i in transactions:
				results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
			response = {}
			response['response'] = results
			response = json.dumps(response)
			return response
		
		if request.method == 'POST' and request.json['type'] == 'staff':
			transactions = db.transactions.find({'done_by' :{'$regex' : query} }).sort([('_id', -1)])
			for i in transactions:
				results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference'],str(i['_id'])])
			response = {}
			response['response'] = results
			response = json.dumps(response)
			return response


	else:
		return redirect('/login')




#Searches for interns and returns results.
@app.route('/search', methods=['GET','POST'])
def search():
	results = []
	query = request.json['query']
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key'  :  key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		search_results = db.intern.find({'name': {'$regex' : query}})
		if search_results != None:
			for i in search_results:
				results.append([i['name'],i['img'],str(i['_id']), i['email'], i['unit_name']])
			response = {}
			response['response'] = results
			response = json.dumps(response)
			return response
		else:
			response = {}
			response['response'] = "No Interns Found "
			response = json.dumps(response)
			return response

	if db.active.find({'key': key }).count() != 0 and usr['type'] == 'unit':
		user = db.unit_holder.find_one({'email'  :  usr['email']})
		search_results = db.intern.find({'name': {'$regex' : query}, 'unit_name':user['unit_name']})
		if search_results != None:
			for i in search_results:
				results.append([i['name'],i['img'],str(i['_id']), i['email'], i['unit_name']])
			response = {}
			response['response'] = results
			response = json.dumps(response)
			return response
		else:
			response = {}
			response['response'] = "No Interns Found "
			response = json.dumps(response)
			return response	
			


	else:
		return redirect('/login')











#Commit Transaction
@app.route("/transaction/money_in")
def transaction_in():
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email'  : user['email']})
		return render_template('money_in.html',user=user)
	else:
		return redirect('/login')



@app.route("/transaction/money_out")
def transaction_out():
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email'  : user['email']})
		return render_template('money_out.html',user=user)
	else:
		return redirect('/login')



#Transaction Money In API
@app.route('/money_in', methods=['POST'])
def money_in():
	email = request.cookies.get('email')
	user = db.staff.find_one({'email'  :  email})
	data={
	"date":strftime("%a, %d %b %Y", gmtime()),
	"intern_name":request.json['intern_name'],
	"amount":int(request.json['amount']),
	"reference":request.json['reference'],
	"type": "money_in",
	"done_by": user['name']
	}
	print data['intern_name']
	
	intern = db.intern.find({'name'  :  data['intern_name']}).count()
	print intern
	if intern != 0:
		intern = db.intern.find_one({'name'  :  data['intern_name']})
		intern['balance'] =intern['balance']+data['amount']
		db.intern.save(intern)
		response = {}
		response['response'] = 'success'
		response = json.dumps(response)
		db.transactions.insert_one(data)
		return response
		
	else:
		response = {}
		response['response'] = 'User Not Found'
		response = json.dumps(response)
		return response


#Transaction Money Out API
@app.route('/money_out', methods=['POST'])
def money_out():
	email = request.cookies.get('email')
	user = db.staff.find_one({'email'  :  email})
	data={
	"date":strftime("%a, %d %b %Y", gmtime()),
	"intern_name":request.json['intern_name'],
	"amount":int(request.json['amount']),
	"reference":request.json['reference'],
	"type":"money_out",
	"done_by": user['name']
	}
	intern = db.intern.find({'name'  :  data['intern_name']}).count()
	if intern == 1:
		intern = db.intern.find_one({'name'  :  data['intern_name']})
		if data['amount'] < intern['balance']:
			intern['balance'] =intern['balance'] - data['amount']
			db.intern.save(intern)
			response = {}
			response['response'] = 'success'
			response = json.dumps(response)
			db.transactions.insert_one(data)
			return response
		else:
			response = {}
			response['response'] = 'Not Enough Balance'
			response = json.dumps(response)
			return response

	else:
		response = {}
		response['response'] = 'User Not Found'
		response = json.dumps(response)
		return response



@app.route('/logout')
def logout():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		db.active.remove({'key':key})
		resp = make_response(redirect('/'))
    	resp.set_cookie('key','',expires=0)
    	resp.set_cookie('email','',expires=0)
    	resp.set_cookie('type','',expires=0)
    	resp.set_cookie('superuser','',expires=0)
    	return resp

@app.route('/approve/interns', methods=['GET','POST'])
def approve_interns():
	email = request.cookies.get('email')
	type_user = request.cookies.get('type')
	user = db.staff.find_one({'email'  :  email})
	if type_user == 'staff':
		interns = db.approve_intern.find()
		intern_list = []
		intern_count = db.approve_intern.find({}).count()
		amount_of_interns = []
		for i in interns:
			intern_list.append([i['name'],i['img'],i['unit_name'],i['_id']])
		i = 0
		while i < intern_count:
			amount_of_interns.append(i)
			i = i+1

		#Approve
		if request.method == 'POST' and request.json['type'] == 'approve':

			#Finding the intern to approve
			approve_intern = db.approve_intern.find_one({'_id':ObjectId(request.json['id'])})

			#Setting Intern Data
			data = {
				"name":approve_intern['name'],
				"unit_name":approve_intern['unit_name'],
				"email":approve_intern['email'],
				"phone_number":approve_intern['phone_number'],
				"start_date":approve_intern['start_date'],
				"end_date":approve_intern['end_date'],
				"balance": 0,
				"img": approve_intern['img'],
				"scheme":[],
				"created_by":approve_intern['created_by']
						}
			#Inserting the intern 
			db.intern.insert_one(data)
			#Deleting intern
			db.approve_intern.delete_one({'_id':ObjectId(request.json['id'])})

			#Logging
			log_data = {
			"intern_name": data['name'],
			"type": "approve_intern",
			"done_by": user['name'],
			"date":strftime("%a, %d %b %Y", gmtime())
			}
			db.log.insert_one(log_data)

			#Find the intern
			data = db.intern.find_one({'name':data['name']})
			data_id = '%s'%(data['_id'])
			response = {}
			response['response'] = 'success_approve'
			response['id'] = data_id
			response = json.dumps(response)
			return response


	#Disapprove
	if request.method == 'POST' and request.json['type'] == 'disapprove':

			#Finding the intern to approve
			approve_intern = db.approve_intern.find_one({'_id':ObjectId(request.json['id'])})
			print approve_intern
			

			#Logging
			log_data = {
			"intern_name": approve_intern['name'],
			"type": "disapprove",
			"done_by": user['name'],
			"date": strftime("%a, %d %b %Y", gmtime())
			}
			#Deleting intern
			db.approve_intern.delete_one({'_id':ObjectId(request.json['id'])})
			db.log.insert_one(log_data)
			response = {}
			response['response'] = 'success_disapprove'
			response = json.dumps(response)
			return response

	return render_template('approve_interns.html',intern=intern_list,user=user,intern_count=amount_of_interns)


@app.route('/backtrack', methods=['GET','POST'])
def backtrack():
	email = request.cookies.get('email')
	user = db.staff.find({'email':email}).count()
	if user != 0:
		user = db.staff.find_one({'email':email})
		data = request.json['id']
		transaction = db.transactions.find({'_id':ObjectId(data)}).count()

		if transaction != 1:
			response = {}
			response['response'] = 'incorrect_id'
			response = json.dumps(response)
			return response

		if transaction == 1:
			transaction = db.transactions.find_one({'_id':ObjectId(data)})
			intern = db.intern.find_one({'name':transaction['intern_name']})


			if transaction['type'] == 'money_in':
				#Check if there is enough money to reverse
				if intern['balance'] < int(transaction['amount']):
					response = {}
					response['response'] = 'not_enough_balance'
					response = json.dumps(response)
					return response

				else:
					intern['balance'] = intern['balance']-int(transaction['amount'])
					db.intern.save(intern)
					data={
							"date":strftime("%a, %d %b %Y", gmtime()),
							"intern_name":transaction['intern_name'],
							"amount":int(transaction['amount']),
							"reference":'undo_transaction',
							"type": "money_out",
							"done_by": user['name']
							}
					db.transactions.insert_one(data)
					response = {}
					response['response'] = 'success'
					response = json.dumps(response)
					return response


			if transaction['type'] == 'money_out':
					intern['balance'] = intern['balance']+int(transaction['amount'])
					db.intern.save(intern)
					data={
						"date":strftime("%a, %d %b %Y", gmtime()),
						"intern_name":transaction['intern_name'],
						"amount":int(transaction['amount']),
						"reference":'undo_transaction',
						"type": "money_in",
						"done_by": user['name']
						}
					db.transactions.insert_one(data)
					response = {}
					response['response'] = 'success'
					response = json.dumps(response)
					return response
		else:
			return 'GTFO'

@app.route('/log', methods=['GET','POST'])
def view_log():
	email = request.cookies.get('email')
	type_user = request.cookies.get('type')
	user = db.staff.find_one({'email'  :  email})
	if type_user == 'staff':
		logs = db.log.find().sort([('_id', -1)])

	else:
		return redirect('/home/unit')
	return render_template('log.html', logs=logs, user=user)
		

@app.route('/superuser', methods=['GET','POST'])
def super_user():
	code = db.code.find().count()
	if code == 0:
		return redirect('/create_super')
	else:
		if request.method == 'POST':
			code = request.json['code']
			super_user_code = db.code.find_one()
			try:
				response = {}
				ph.verify(super_user_code['code'],code)
				active_user = {
				'code': key_gen()
				}
				response['response'] = 'success'
				response['code'] = active_user['code']
				db.active.insert_one(active_user)

				response = json.dumps(response)
				return response
			except:
				response = {}
				response['response'] = 'failure'
				response = json.dumps(response)
				return response  
	return render_template('login_super.html')

@app.route('/create_super', methods=["GET","POST"])
def create_super():
	callback = ''
	code = db.code.find().count()
	if code != 0:
		return redirect('/superuser')
	else:
		if request.method == 'POST':
			data = {
			'code' : ph.hash(request.form['code'])
			}
			db.code.insert_one(data)
			callback = 'Successfully created the superuser code'
	return render_template('create_super.html',callback=callback)

@app.route('/home/superuser', methods=['GET','POST'])
def home_superuser():
	cookie = request.cookies.get('superuser')
	user = db.active.find({'code':cookie}).count()
	print cookie
	if user != 0:
		staff_to_approve = db.approve_staff.find().count()
		unit_holders_to_approve = db.approve_unit_holder.find().count()
		all_staff = db.staff.find()
		all_units = db.unit_holder.find()
	else:
		return redirect('/superuser')
	return render_template('super_user.html',staff=staff_to_approve,unit_holder=unit_holders_to_approve)

@app.route('/approve/superuser/staff', methods=['GET','POST'])
def superuser_approve_staff():
	cookie = request.cookies.get('superuser')
	if cookie == None:
		return redirect('/superuser')
	user = db.active.find({'code':cookie}).count()
	if user != 0:
		type = 'Staff'
		type_url = 'staff'
		to_approve = db.approve_staff.find()
		if request.method == 'POST' and request.json['type'] == 'approve':
			#finding the staff
			staff = db.approve_staff.find_one({'_id':ObjectId(request.json['id'])})

			#setting data
			data ={
			"name":staff['name'],
			"password": staff['password'],
			"email":staff['email'],
			"phone_number":staff['phone_number']
			}

			db.staff.insert_one(data)
			db.approve_staff.delete_one({'_id':ObjectId(request.json['id'])})
			response = {}
			response['response'] = 'success'
			response = json.dumps(response)
			return response


		if request.method == 'POST' and request.json['type'] == 'disapprove':
			unit = db.approve_staff.find_one({'_id':ObjectId(request.json['id'])})
			db.approve_staff.delete_one({'_id':ObjectId(request.json['id'])})
			response = {}
			response['response'] = 'success'
			response = json.dumps(response)
			return response  
	else:
		return redirect('/superuser')
	return render_template('superuser_approve.html',type=type,to_approve=to_approve,type_url=type_url)

@app.route('/approve/superuser/unit', methods=['GET','POST'])
def superuser_approve_unit():
	cookie = request.cookies.get('superuser')
	if cookie == None:
		return redirect('/superuser')
	user = db.active.find({'code':cookie}).count()
	if user != 0:
		type = 'Unit Holders'
		type_url = 'unit'
		to_approve = db.approve_unit_holder.find()
		if request.method == 'POST' and request.json['type'] == 'approve':
			#finding the staff
			unit = db.approve_unit_holder.find_one({'_id':ObjectId(request.json['id'])})

			#setting data
			data ={
			"unit_name":unit['unit_name'],
			"name":unit['name'],
			"password": unit['password'],
			"email":unit['email'],
			"phone_number":unit['phone_number']
			}

			db.unit_holder.insert_one(data)
			db.approve_unit_holder.delete_one({'_id':ObjectId(request.json['id'])})
			response = {}
			response['response'] = 'success'
			response = json.dumps(response)
			return response

		if request.method == 'POST' and request.json['type'] == 'disapprove':
			unit = db.approve_unit_holder.find_one({'_id':ObjectId(request.json['id'])})
			db.approve_unit_holder.delete_one({'_id':ObjectId(request.json['id'])})
			response = {}
			response['response'] = 'success'
			response = json.dumps(response)
			return response
	else:
		return redirect('/superuser')
	return render_template('superuser_approve.html',type=type,type_url=type_url,to_approve=to_approve)


@app.route('/superuser/list', methods=['GET','POST'])
def list():
	cookie = request.cookies.get('superuser')
	if cookie == None:
		return redirect('/superuser')
	user = db.active.find({'code':cookie}).count()
	if user != 0:
		list_unit = []
		list_staff = []
		unit_holders = db.unit_holder.find()
		staff = db.staff.find()
		for i in unit_holders:
			list_unit.append([i['name'],i['email'], i['unit_name'],str(i['_id'])])
		for i in staff:
			list_staff.append([   i['name'],i['email'],str(i['_id'])])



	return render_template('superuser_admin_list.html',unit_holder=list_unit,staff=list_staff)	


@app.route('/superuser/add/staff')
def add_staff_super():
	cookie = request.cookies.get('superuser')
	if cookie == None:
		return redirect('/superuser')
	user = db.active.find({'code':cookie}).count()
	if user != 0:
		pass
	return render_template('add_staff.html')

if __name__ == "__main__":
	configure_uploads(app, photos)
	app.run()