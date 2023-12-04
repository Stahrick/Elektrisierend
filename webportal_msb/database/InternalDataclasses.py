from dataclasses import dataclass, field, asdict
from uuid import uuid4

@dataclass
class Contract:
    _id : str = field(init = False, repr = False)
    date : str #TODO what format
    personal_info : str
    iban : str 
    em_id : str
    state : str
    city : str
    zip_code : int
    address : str

    def __post_init__(self):
        self._id = str(uuid4())

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

@dataclass
class Em:
    _id : str = field(init = False, repr = False)
    em_data : float
    em_consumption : float
    em_cost : float
    hist_id : str

    def __post_init__(self):
        self._id = str(uuid4())

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

@dataclass
class HistData:
    _id : str = field(init = False, repr = False)
    data : list

    def __post_init__(self):
        self._id = str(uuid4())

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

@dataclass
class Account:
    _id : str = field(init = False, repr = False)
    role : str
    username : str 
    pw_hash : int
    first_name : str
    last_name : str
    email : str 
    phone : int 
    state : str
    city : str 
    zip_code : int
    address : str 
    contract_id : str

    def __post_init__(self):
        self._id = str(uuid4())


    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


    #moved em_reading and em_id to Contract

@dataclass
class Ticket:
    _id: str = field(init = False, repr = False)
    title: str
    opened: str
    status: str
    device_uuid: str
    description: str
    opened_by: str
    comments : list

    def __post_init__(self):
        self._id = str(uuid4())


    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
    