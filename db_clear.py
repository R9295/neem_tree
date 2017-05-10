from pymongo import *
client = MongoClient()
db = client.neem_tree

#Interns
db.intern.delete_many({})


#Unit Holder
db.unit_holder.delete_many({})
db.approve_unit_holder.delete_many({})

#Staff
db.staff.delete_many({})
db.approve_staff.delete_many({})

#Active
db.active.delete_many({})

#ransactions
db.transactions.delete_many({})

#log
db.log.delete_many({})

#approve interns 
db.approve_intern.delete_many({})

#code 
db.code.delete_many({})