import requests
from uuid import uuid4

url = 'http://localhost:25565'

def place_order():
    new_uuid = str(uuid4())
    data = { "uuid": new_uuid}
    r = requests.post(f"{url}/meter/order/", json=data)
    if r.status_code == 200:
        return new_uuid
    else:
        return False 

def swap_cert(uuid, cert):
    r = requests.post(f"{url}/meter/{uuid}/swap-certificate", file=cert)
    if r.status_code == 200:
        return True
    else:
        return False


if __name__ == "__main__":
    print(place_order())