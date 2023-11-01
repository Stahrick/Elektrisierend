from database.DatabaseUtil import MoronDB
from database.InternalDataclasses import Account
class AccountHandler:

    db : MoronDB    
    collection = 'accounts'

    def __init__(self, username, password, dbname, collection = 'accounts'):
        self.db = MoronDB(27018,username,password,dbname)
        if collection:
            self.collection = collection
        print()
    def create_account(self, acc : Account):
        return self.db.insert_item(collection = self.collection, data= acc)
    
    def delete_account_by_id(self, id : int):
        return self.db.delete_item_by_id(self.collection, id) 
    
    def get_account_by_id(self, id):
        return self.db.get_item_by_id(self.collection, id)   
     
    #!could return a list of users    
    def get_account_by_username(self, username):
        return self.db.get_items(self.collection, {"username" : username})
    
    def update_account_by_id(self, id, data : dict):
        return self.db.update_item_by_id(self.collection, id, data)
    
    def update_account_by_username(self, username,data):
        return self.db.update_item_by_filter(self.collection, {"username" : username}, data)

#usage example
"""
handler = AccountHandler("username","password","dbname")
:)
#"""