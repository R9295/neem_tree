from flask import Flask,render_template,redirect,request,make_response,redirect,url_for
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
from bson.objectid import ObjectId

#Connecting to DB
client = MongoClient()
db = client.neemtree


# id_generator
def key_gen(size=10, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

ph = PasswordHasher()

app = Flask(__name__)

#Login for Unit Holder and Neem Tree Staff
@app.route("/")
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
	user = 0
	unit = 9
	if request.method == 'POST':
		#Verify login form data

#The way the login works is it checks if the email exists in either unit holder or neem tree staff
#If it's in either it logs in, and inserts a hashed key in the 'active' users DB, the same key is in your cookies,
#This makes sure it's you logging in and on one device only.

		user = db.staff.find({'email': request.json['email']}).count()
		unit = db.unit_holder.find({'email': request.json['email']}).count()
        if user  == 1:
			print 'xd'
			user = db.staff.find_one({'email': request.json['email']})
			if ph.verify(user['password'],request.json['password']) == True:

				key = key_gen()
				hashed_key = hashpw(key,gensalt())
				active_user = {
                    'email' : request.json['email'],
                    'key'  : hashed_key,
                    'type'  : 'staff'
                }
				db.active.insert_one(active_user)
				response = {
				"response": "success",
				"email":request.json['email'],
				"key": hashed_key,
				"type":"staff"
				}
				

		
				response = json.dumps(response)
				
				return response


        #elif unit == 1:
		#	user = db.unit_holder.find_one({'email': request.json['email']})
		#	if ph.verify(user['password'],request.json['password']) == True:

			#	key = key_gen()
			#	hashed_key = hashpw(key,gensalt())
			#	active_user = {
             #       'email' : request.json['email'],
              #      'key'  : hashed_key,
              #      'type'  : 'unit'
              #  }
			#	response = {
			#	"response": "success",
			#	"email":request.json['email'],
			#	"key": hashed_key,
			#	"type":"unit"
			#	}
			#	response = json.dumps(response)
			#	return response
			
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
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		return render_template('home_staff.html',user=user)
	#else:
		#return redirect('/login')



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
	"phone_number":request.json['phone_number']
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


@app.route('/add/intern')
def add_an_intern():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		return render_template('add_intern.html',user=user)

#Edit Intern Page
@app.route('/edit/intern/<id>')
def edit_an_intern(id):
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		return render_template('edit_intern.html',user=user)

#Intern List 
@app.route('/interns')
def intern_list():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		interns = db.intern.find()
		return render_template('interns.html',user=user,interns=interns)

#Individual Intern
@app.route('/<id>')
def individual_intern(id):
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		intern = db.intern.find_one({'_id': ObjectId(id)})
		print intern
		return render_template('intern_page.html',user=user,intern=intern)


#Add Intern API
@app.route("/add_intern", methods=['POST'])
def add_intern():
	data = {
	"name":request.json['name'],
	"email":request.json['email'],
	"phone_number":request.json['phone_number'],
	"unit_name":request.json['unit_name'],
	"img":request.json['img'],
	"start_date":request.json['start_date'],
	"end_date":None,
	"balance": 0

		}
	try:
		db.intern.insert_one(data)
		response = {}
		response['response'] = 'success'
		response = json.dumps(response)
		return response
	except:
		response = {}
		response['response'] = "failure"
		response = json.dumps(response)
		return response	


#Edit Intern API
@app.route("/edit_intern", methods=['POST'])
def edit_intern():
	pass


#Remove Intern API
@app.route("/remove_intern", methods=['POST'])
def remove_intern():
	pass



#Transactions


#View Transactions
@app.route('/view_transactions')
def view_transactions():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		transactions = db.transactions.find()
		return render_template('view_transactions.html',user=user,transactions=transactions)


#Commit Transaction
@app.route("/transaction")
def transaction():
	key = request.cookies.get('key')
	error = None
	if db.active.find({'key' : key}).count() != 0:
		user = db.active.find_one({'key' : key})
		return render_template('transaction.html',user=user)

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
	
	intern = db.intern.find({'name'  :  data['intern_name']}).count()
	if intern == 1:
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
		intern['balance'] =intern['balance'] - data['amount']
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=5000)