from pymongo import *
client = MongoClient()
db = client.neem_tree

#Interns
print str(db.intern.find().count())+ '  Interns'

'''
#Unit Holder
print db.unit_holder.find().count()+ '  Unit Holders'
print db.approve_unit_holder.find().count()+ '  Approve Unit Holder'

#Staff
print db.staff.find().count()+ '  Staff'
print db.approve_staff.find().count()+  ' Approve Staff'

#Active
print db.active.find().count()+ '   Active'

#ransactions
print db.transactions.find().count()+ '   Transactions'

#log
print db.log.find().count()+ '  Log'

#approve interns 
print db.approve_intern.find().count()+ '  Approve Interns'
'''