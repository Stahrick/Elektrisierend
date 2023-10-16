from dataclasses import dataclass


@dataclass
class Contract:
    _id : int
    date : str #TODO what format
    personal_info : str
    em_id : int
    em_data : list
    em_consumption : int
    em_cost : int

@dataclass
class Account:
    _id : int
    username : str 
    pw_hash : int
    pw_salt : int
    first_name : str
    last_name : str
    email : str 
    iban : str 
    phone : int 
    city : str 
    zip_code : int
    address : str 
    contract : Contract
    #moved em_reading and em_id to Contract

