import base64

import requests
import os
from uuid import uuid4
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
from config import meter_url, own_url, mycert, root_ca

def place_order():
    new_uuid = str(uuid4())
    data = { "uuid": new_uuid}
    r = requests.post(f"{meter_url}/meter/order/", json=data, cert=mycert, verify='RootCA.crt')
    if r.status_code == 200:
        return new_uuid
    else:
        return False 

def swap_cert(uuid, cert):
    r = requests.post(f"{meter_url}/meter/{uuid}/swap-certificate", file=cert, cert=mycert)
    if r.status_code == 200:
        return True
    else:
        return False

def sign_cert(csr):
    pem_data = ''
    with open(mycert[1], 'rb') as pem_in:
        pem_data = pem_in.read()
    key = load_pem_private_key(pem_data, password=None)
    #key = rsa.generate_private_key(
    #    public_exponent=65537,
    #    key_size=2048,
    #)

    with open(mycert[0], 'rb') as cert_file:
        cert_data = cert_file.read()

    # Parse the certificate
    tmp = x509.load_pem_x509_certificate(cert_data)
    
    extension = tmp.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier)

    # Access the attributes of the AuthorityKeyIdentifier extension
    authority_key_identifier = extension.value

    # Access individual attributes if needed
    key_identifier = authority_key_identifier.key_identifier
    a_issuer = authority_key_identifier.authority_cert_issuer
    serial_number = authority_key_identifier.authority_cert_serial_number

    issuer = tmp.issuer
    csr_data = x509.load_pem_x509_csr(csr)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, csr_data.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value ),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr_data.subject.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value ),
        x509.NameAttribute(NameOID.LOCALITY_NAME, csr_data.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value ),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, csr_data.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value ),
        x509.NameAttribute(NameOID.COMMON_NAME, csr_data.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value ),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        csr_data.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        # Our certificate will be valid for 10 days
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    )
    cert = cert.add_extension(
        x509.AuthorityKeyIdentifier(key_identifier=key_identifier, authority_cert_issuer=a_issuer, authority_cert_serial_number=serial_number),  # Replace 'authority_key_identifier' with your object
        critical=False
    )
    cert = cert.sign(key, hashes.SHA256())
    # Write our certificate out to disk.
    cert_string = ''
    with open(mycert[0], 'r') as f:
        cert_string = f.read()
    root_string = ''
    with open(root_ca, 'r') as f:
        root_string = f.read()
    print(root_string + cert_string + cert.public_bytes(serialization.Encoding.PEM).decode('utf-8'))
    return cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')


def gen_rsa_keypair():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    with open("../sign_test_key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    pub_key = key.public_key()
    with open("../sign_test_key.pub", "wb") as f:
        f.write(pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def send_service_worker_mails(mail_texts: list[list[str, str]]):
    """
    Sends mails to the service worker endpoint on the smart meter application
    :param mail_texts: Array containing all mails that should be sent. Every mail has the structure [subject, text]
    :return:
    """
    service_worker_mail_endpoint = f"{meter_url}/service-worker/receive-mails"
    r = requests.post(service_worker_mail_endpoint, json=mail_texts ,cert=mycert, verify='RootCA.crt')
    if r.status_code != 200:
        print(f"Send mail failed. Statuscode {r.status_code} - {r.text}")

def send_registration_mail(meter_uuid):
    code = base64.b64encode(os.urandom(10)).decode()
    # TODO Bind code with contract
    # TODO adjust url
    msb_url = f"{own_url}/meter"
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)
    payload = {"iss": "msb", "aud": meter_uuid, "exp": exp, "uuid": meter_uuid, "code": code, "url": msb_url }

    with open("./sign_test_key.pem", "rb") as fi:
        priv_key = serialization.load_pem_private_key(
            fi.read(), password=None, backend=default_backend()
        )
    token = jwt.encode(payload, priv_key, "RS512")
    send_service_worker_mails([[f"Registration-Code for meter[{meter_uuid}] installation",
                                                           f"{token}"]])




if __name__ == "__main__":
    # csr = ''
    # with open('test.crt', 'rb') as f:
    #     csr = f.read()
    # print(sign_cert(csr))
    #gen_rsa_keypair()
    send_registration_mail("5780abd6-2a40-48ef-a21d-25b5fcd9224a")
