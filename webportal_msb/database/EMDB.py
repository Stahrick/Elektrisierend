from database.DatabaseUtil import MoronDB
from database.InternalDataclasses import Em
class EmHandler:

    db : MoronDB    
    collection = 'ems'

    def __init__(self, username, password, dbname, collection = 'ems'):
        self.db = MoronDB(27018,username,password,dbname)
        if collection:
            self.collection = collection
        print()
    def create_Em(self, c : Em) -> bool:
        try:
            return self.db.insert_item(collection = self.collection, data= c.dict())
        except:
            return False
    
    def delete_Em_by_id(self, id : int) -> bool: 
        try:
            return self.db.delete_item_by_id(self.collection, id) 
        except:
            return False
    
    def get_Em_by_id(self, id) -> Em:
        try:
            return self.db.get_item_by_id(self.collection, id)  
        except:
            return False 
    def get_all(self):
        return self.db.get_items_all(self.collection)
    
    def update_Em_by_id(self, id, data : dict) -> bool:
        try:
            return self.db.update_item_by_id(self.collection, id, data)
        except:
            return False

