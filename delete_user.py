from pymongo import *
client = MongoClient()
db = client.neem_tree

email = raw_input('Enter the email ID of person to delete    ')
db_type = raw_input('Enter 1 for unit holder, 2 for staff, 3 for intern    ')


if db_type == '1':
	data = db.unit_holder.find({'email':email}).count()
	if data != 0:
		print 'found results for the email, deleting'
		db.unit_holder.delete_one({'email':email})
	else:
		print 'No results found'

if db_type == '2':
	data = db.staff.find({'email':email}).count()
	if data != 0:
		print 'found results for the email, deleting'
		db.staff.delete_one({'email':email})
	else:
		print 'No results found'

if db_type == '3':
	data = db.intern.find({'email':email}).count()
	if data != 0:
		print 'found results for the email, deleting'
		db.intern.delete_one({'email':email})
	else:
		print 'No results found'

