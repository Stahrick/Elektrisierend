from dataclasses import dataclass, field, asdict
from uuid import uuid4

@dataclass
class Contract:
    _id : int
    date : str #TODO what format
    personal_info : str
    em_data : list
    em_consumption : int
    em_cost : int

@dataclass
class Account:
    _id : int = field(init = False, repr = False)
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

    def __post_init__(self):
        self._id = uuid4()

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


    #moved em_reading and em_id to Contract

