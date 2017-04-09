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



#Connecting to DB

client = MongoClient()
db = client.neem_tree




# id_generator
def key_gen(size=10, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

ph = PasswordHasher()

app = Flask(__name__)



#Configuring where photos should be uploaded.
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = '/home/www/neem_tree/static/img/'



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
        if user  == 1:
			
			user = db.staff.find_one({'email': request.json['email']})
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


        elif unit == 1:
			
			user = db.unit_holder.find_one({'email': request.json['email']})
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
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email':user['email']})
		return render_template('home_staff.html',user=user)
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
	data ={
	"name":request.json['name'],
	"password": ph.hash(request.json['password']),
	"email":request.json['email'],
	"phone_number":request.json['phone_number']
	}

	try:
		db.staff.insert_one(data)
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
	data ={
	"unit_name":request.json['unit_name'],
	"password": ph.hash(request.json['password']),
	"name":request.json['person_name'],
	"email":request.json['email'],
	"phone_number":request.json['phone_number'],
	}
	try:
		db.unit_holder.insert_one(data)
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
					email = request.cookies.get('email')
					user = db.unit_holder.find_one({'email'  : email })
					filename = photos.save(request.files['img'])
					data = {
					"name":request.form['name'],
					"unit_name":user['unit_name'],
					"email":request.form['email'],
					"phone_number":request.form['phone_number'],
					"start_date":request.form['start_date'],
					"end_date":None,
					"balance": 0,
					"img": filename,
					"scheme":[]
					}
					
					try:
						db.intern.insert_one(data)
						return redirect('/interns')			
					except:
						return "Couldn't create intern. Contact admin"

		return render_template('add_intern.html',user=user,error=error)
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
			filename = photos.save(request.files['img'])
			return filename

		#	if len(request.form['email']) == 0:
		#				error = 'Invalid email'

		#	if len(request.form['name'])  == 0:
		#				error = 'Invalid Name'

				
		#	if request.form['phone_number'].isdigit() != True or len(str(request.form['phone_number'])) != 10 :
         #   			error = 'Invalid phone number'
         	
		#	if error == '':
		#		email = request.cookies.get('email')
		#		user = db.staff.find_one({'email'  : email })
		#3		filename = photos.save(request.files['img'])
		#		data = {
		#		"name":request.form['name'],
		#		"unit_name":request.form['unit_name'],
		#		"email":request.form['email'],
		#		"phone_number":request.form['phone_number'],
		#		"start_date":request.form['start_date'],
		#		"end_date":None,
		#		"balance": 0,
		#		"img": filename,
		#		"scheme":[]
		#		}
		#		
		#	
		#		db.intern.insert_one(data)
		#		return redirect('/interns')			
			
		return render_template('add_intern_staff.html',user=user,error=error)
	else:
		return redirect('/login')


@app.route('/add_scheme/<id>', methods=['GET','POST'])
def add_scheme(id):
	key = request.cookies.get('key')
	email = request.cookies.get('email')
	error = None

	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		if db.unit_holder.find({'email': user['email']}).count() != 0:
			return redirect('/home/unit')
		else:
			user = db.intern.find_one({'_id': ObjectId(id)})
			active_user = db.staff.find_one({'email':email})

		if request.method == 'POST':


			if request.form.get('snack'):
				start_date = request.form['start_date']
				start_year = start_date[0:4]
				start_month = start_date[5:7]
				start_day = start_date[8:10]
				start_date= start_day+'/'+start_month+'/'+start_year

				end_date = request.form['end_date']
				end_year = end_date[0:4]
				end_month = end_date[5:7]
				end_day = end_date[8:10]
				end_date= end_day+'/'+end_month+'/'+end_year

				data = {
				'type' : 'snack',
				'start_date' : start_date,
				'end_date' : end_date
				}
				user['scheme'].append(data)
			else:
				snack = False



			if request.form.get('breakfast'):
				start_date = request.form['start_date']
				start_year = start_date[0:4]
				start_month = start_date[5:7]
				start_day = start_date[8:10]
				start_date= start_day+'/'+start_month+'/'+start_year

				end_date = request.form['end_date']
				end_year = end_date[0:4]
				end_month = end_date[5:7]
				end_day = end_date[8:10]
				end_date= end_day+'/'+end_month+'/'+end_year

				data = {
				'type' : 'breakfast',
				'start_date' : start_date,
				'end_date' : end_date
				}
				user['scheme'].append(data)
			else:
				breakfast = False


			if request.form.get('lunch'):
				start_date = request.form['start_date']
				start_year = start_date[0:4]
				start_month = start_date[5:7]
				start_day = start_date[8:10]
				start_date= start_day+'/'+start_month+'/'+start_year

				end_date = request.form['end_date']
				end_year = end_date[0:4]
				end_month = end_date[5:7]
				end_day = end_date[8:10]
				end_date= end_day+'/'+end_month+'/'+end_year

				data = {
				'type' : 'lunch',
				'start_date' : start_date,
				'end_date' : end_date
				}
				user['scheme'].append(data)
			else:
				lunch = False

			if request.form.get('dinner'):
				start_date = request.form['start_date']
				start_year = start_date[0:4]
				start_month = start_date[5:7]
				start_day = start_date[8:10]
				start_date= start_day+'/'+start_month+'/'+start_year

				end_date = request.form['end_date']
				end_year = end_date[0:4]
				end_month = end_date[5:7]
				end_day = end_date[8:10]
				end_date= end_day+'/'+end_month+'/'+end_year

				data = {
				'type' : 'dinner',
				'start_date' : start_date,
				'end_date' : end_date
				}
				user['scheme'].append(data)
			else:
				dinner = False
			db.intern.save(user)
			return redirect('/%s'%(id))




			
		return render_template('add_scheme.html', active_user=active_user,user=user )


@app.route('/remove/scheme', methods=['GET','POST'])
def remove_scheme():
	interns = db.intern.find_one({'name' : request.json['intern_name']})
	type = request.json['type']
	for i in intern['scheme']:
		if i['type'] == type:
			index = intern['scheme'].index(i)
			print index
			intern['scheme'].pop(index)
			
		db.intern.save(interns)
	return redirect('/%s'%(intern['_id']))

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
@app.route('/<id>')
def individual_intern(id):
	key = request.cookies.get('key')
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
				user = db.staff.find_one({'email'  :  request.cookies.get('email')})
				if user['unit_name'] == intern['unit_name']:
					pass
				else:
					return redirect('/home/unit')

		return render_template('intern_page.html',user=user,intern=intern)
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
	if db.active.find({'key'  :  key}).count() != 0:
		user = db.active.find_one({'key'  :  key})
		type = request.cookies.get('type')
		#Checking if user has right to edit intern
		if type == 'staff':
			user = db.staff.find_one({'email'  :  user['email']})
			intern = db.intern.find_one({'_id' : ObjectId(id)})
		if type == 'unit':
			user = db.unit_holder.find_one({'email'  :  user['email']})
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
			except KeyError:
				pass
				
			try:
				end_date = request.json['end_date']
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
			return jsonify({'response'  : 'success'})



		return render_template('edit_individual.html',user=user,intern=intern)
	

	else:
		return redirect('/login')
		


#View Transactions
@app.route('/view_transactions')
def view_transactions():
	key = request.cookies.get('key')
	error = None
	usr = db.active.find_one({'key' : key})
	if db.active.find({'key' : key}).count() != 0 and usr['type'] == 'staff':
		user = db.active.find_one({'key' : key})
		user = db.staff.find_one({'email'  : user['email']})
		transactions = db.transactions.find().sort([('_id', -1)])
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
		transactions = db.transactions.find({'intern_name' :{'$regex' : query} }).sort([('_id', -1)])
		for i in transactions:
			results.append([i['amount'],i['type'],i['intern_name'],i['date'],i['done_by'],i['reference']])
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
    	return resp

if __name__ == "__main__":
	configure_uploads(app, photos)
	app.run(debug=True)