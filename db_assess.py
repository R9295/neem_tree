from pymongo import *
client = MongoClient()
db = client.neem_tree

#Interns
print db.intern.find().count()


#Unit Holder
print db.unit_holder.find().count()
print db.approve_unit_holder.find().count()

#Staff
print db.staff.find().count()
print db.approve_staff.find().count()

#Active
print db.active.find().count()

#ransactions
print db.transactions.find().count()

#log
print db.log.find().count()

#approve interns 
print db.approve_intern.find().count()
'''