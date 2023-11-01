from database.DatabaseUtil import MoronDB
from database.InternalDataclasses import Account, Contract
class AccountHandler:

    db : MoronDB    
    collection = 'accounts' 

    def __init__(self, username, password, dbname, collection = 'accounts'):
        self.db = MoronDB(27018,username,password,dbname)
        if collection:
            self.collection = collection
        print()
    def create_account(self, acc : Account):
        try:
            print(acc)
            return self.db.insert_item(collection = self.collection, data= acc.dict())
        except:
            return False
    
    def delete_account_by_id(self, id : int):
        try:
            return self.db.delete_item_by_id(self.collection, id) 
        except:
            return False
    
    def get_account_by_id(self, id):
        try:
            return self.db.get_item_by_id(self.collection, id)  
        except:
            return False 
     
    #!could return a list of users    
    def get_account_by_username(self, username):
        try:
            return self.db.get_items(self.collection, {"username" : username})
        except:
            return False
    
    def update_account_by_id(self, id, data : dict):
        try:
            return self.db.update_item_by_id(self.collection, id, data)
        except:
            return False
    
    def update_account_by_username(self, username,data):
        try:
            return self.db.update_item_by_filter(self.collection, {"username" : username}, data)
        except:
            return False

#usage example
"""
handler = AccountHandler("username","password","dbname")
:)
#"""