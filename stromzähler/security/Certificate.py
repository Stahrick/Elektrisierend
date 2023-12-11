
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def create_X509_csr(uuid) -> (str, str):
    # Generate key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    # TODO check if folder exist, otherwise create
    priv_path = str(Path(__file__).parent / f"../metercerts/{uuid}.key")
    with open(priv_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Mannheim"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Mannheim"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MSB"),
        x509.NameAttribute(NameOID.COMMON_NAME, uuid),
    ])
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Mannheim"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Mannheim"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MSB"),
        x509.NameAttribute(NameOID.COMMON_NAME, uuid),
    ])).add_extension(
        x509.SubjectAlternativeName([
            # Describe what sites we want this certificate for.
            x509.DNSName(u"localhost"),
        ]),
        critical=False,
        # Sign the CSR with our private key.
    ).sign(key, hashes.SHA256())

    # Save cert
    #with open("./csr.pem", "wb") as f:
    #    f.write(csr.public_bytes(serialization.Encoding.PEM))

    return priv_path, csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')
