from database.DatabaseUtil import MoronDB
from database.InternalDataclasses import Ticket
class TicketHandler:

    db : MoronDB    
    collection = 'tickets'

    def __init__(self, username, password, dbname, collection = 'tickets'):
        self.db = MoronDB(27018,username,password,dbname)
        if collection:
            self.collection = collection
        print()
    def create_Ticket(self, c : Ticket) -> bool:
        try:
            return self.db.insert_item(collection = self.collection, data= c.dict())
        except:
            return False
    
    def delete_Ticket_by_id(self, id : int) -> bool: 
        try:
            return self.db.delete_item_by_id(self.collection, id) 
        except:
            return False
    
    def get_Ticket_by_id(self, id) -> Ticket:
        try:
            return self.db.get_item_by_id(self.collection, id)  
        except:
            return False 
    def get_all(self):
        return self.db.get_items_all(self.collection)
    
    def update_Ticket_by_id(self, id, data : dict) -> bool:
        try:
            return self.db.update_item_by_id(self.collection, id, data)
        except:
            return False

