from pymongo import *
client = MongoClient()
db = client.neem_tree

#Interns
db.intern.delete_many({})
db.interns.delete_many({})

#Unit Holder
db.unit_holder.delete_many({})

#Staff
db.staff.delete_many({})

#Active
db.active.delete_many({})

#Transactions
db.transactions.delete_many({})

