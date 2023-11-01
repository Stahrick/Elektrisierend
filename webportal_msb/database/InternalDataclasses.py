from dataclasses import dataclass, field


@dataclass
class Contract:
    _id : str
    date : str #TODO what format
    personal_info : str
    em_data : list
    em_consumption : str
    em_cost : str

@dataclass
class Account:
    _id : str = field(init = False)
    username : str 
    pw_hash : str
    pw_salt : str
    first_name : str
    last_name : str
    email : str 
    iban : str 
    phone : str 
    city : str 
    zip_code : str
    address : str 
    contract : Contract
    #moved em_reading and em_id to Contract

