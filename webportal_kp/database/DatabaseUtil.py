from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

ip = getenv('DBIP')
class MoronDB:

   client = None
   db = None

   def __init__(self, port, username, password,dbname):
      uri =  f"mongodb://{username}:{password}@{ip}:{port}/{dbname}?authSource=admin"
      self.client = MongoClient(uri) 
      self.db = self.client[dbname]

   def insert_item(self, collection, data):
      if type(collection) == str:
         collection = self.get_collection(collection, self.db)

      result = collection.insert_one(data)
      return { "id" : result.inserted_id, "acknowledged" : result.acknowledged}

   def insert_items(self, collection, data):
      if type(collection) == str:
         collection = self.get_collection(collection, self.db)
      result = collection.insert_many(data)
      return { "ids" : result.inserted_ids, "acknowledged" : result.acknowledged}
   
   def create_collection(self, name, database = None):
      if(database):
         db = self.get_database(database)
         collection = db[name]
      elif (self.db):         
         collection = self.db[name]
      return collection
   
   def create_collection_with_data(self,database, name, data):
      collection = self.create_collection(name, database = database)
      if not (isinstance(data,list)):
         return self.insert_item(collection, data)
      if (isinstance(data,list)):
         return self.insert_items(collection, data)
      else: 
         print("wtf are you doing")

   def get_database(self,database):
      return self.client[database]
   
   def get_collection(self, name, database = None):
      if (database == None):
         db = self.get_database(database)
         return db[name]
      
      return self.db[name]   
   #returns all that match the provided document 
   def get_items(self, collection_name : str , data):
      collection = self.get_collection(collection_name, self.db)
      return list(collection.find(data))
      
   def get_item_by_id(self, collection_name : str , id):
      collection = self.get_collection(collection_name, self.db)
      return collection.find_one({"_id": id})
   
   def get_items_by_ids(self, collection_name : str , ids):
      collection = self.get_collection(collection_name, database = self.db)
      return collection.find({"_id": id})
   
   def delete_item_by_id(self, collection_name : str, id):
      collection = self.get_collection(collection_name, self.db)
      return collection.delete_one({"_id": id})
   
   #updates the entity and retains all old keys that are not included in data
   #if the entity with the given id is not found, create entity instead
   def update_item_by_id(self, collection_name : str ,id, data):
      orig = self.get_item_by_id(collection_name,id)
      if orig:
         cache = {}
         for key in orig.keys():
            if key in data.keys():
               cache[key] = data[key]
               continue
            cache[key] = orig[key]
      else: 
         cache = data
      collection = self.get_collection(collection_name,self.db)
      return collection.update_one({"_id": id},{"$set":cache}, upsert = True).acknowledged 
   
   #!!!MEANT TO UPDATE A SINGLE ITEM BY POSSIBLY AMBIGUOUS FILTER
   #if entity is not found, stop
   def update_item_by_filter(self, collection_name : str, filter, data):
      orig = self.get_items(collection_name,filter)
      if type(orig) == list and len(orig)>1:
         return {"acknowledged": False, "error": "filter didnt return a unique item"}
      if orig:
         orig = orig[0]
         cache = {}
         for key in orig.keys():
            if key in data.keys():
               cache[key] = data[key]
               continue
            cache[key] = orig[key]
            collection = self.get_collection(collection_name,self.db)
         return collection.update_one({"_id": orig['_id']},{"$set":cache}, upsert = True).acknowledged
      else: 
         return {"acknowledged": False, "error": "filter didnt return any (single) item"}
      
   

   def update_items_by_ids(self, collection_name : str ,id : list, data : list):
      pass

   def put_item_by_id(self, collection_name : str ,id, data):
      pass

