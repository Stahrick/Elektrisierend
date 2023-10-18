from DatabaseUtil import MoronDB
from InternalDataclasses import Account
from json import loads
class AccountHandler:

    db : MoronDB
    collection = 'Accounts'
    db_name = 'Stromanbieter'

    def __init__(self, port, hostname, dbname, collection = None):
        self.db = MoronDB(port, hostname,dbname = dbname)
        if collection:
            self.collection = collection
    def create_account(self, acc : Account):
        return self.db.insert_item(collection = self.collection, data= acc)
    def delete_account_by_id(self, id : int):
        return self.db.delete_item_by_id(self.collection, id) 
    def get_account_by_id(self, id):
        return self.db.get_item_by_id(self.collection, id)
    def update_account_by_id(self, id, data : any):
        return self.db.update_item_by_id(self.collection, id, data)

#usage example
"""

handler = AccountHandler(27017,'localhost', "db")
with open("test.json") as file:
    id = handler.create_account(loads(file.read()))['id']
    print(handler.get_account_by_id(id))
with open("test2.json") as file:
    print(handler.update_account_by_id(id,loads(file.read())))
with open("test3.json") as file:
    print(handler.update_account_by_id(id,loads(file.read())))
    print(handler.delete_account_by_id(id))
    """
