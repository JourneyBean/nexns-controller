from typing import TYPE_CHECKING
import dns.rdataclass
import dns.rdatatype
import dns.name
import dns.rdata
import dns.rdtypes
import dns.rdataset
import dns.rrset
import dns.dnssec
import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import (
    PrivateKeyTypes,
    PublicKeyTypes,
)

if TYPE_CHECKING:
    from .models import RRset


def generate_ecdsa_key_pair() -> 'tuple[PublicKeyTypes, PrivateKeyTypes]':
    key = paramiko.ECDSAKey.generate(bits=256)
    return key.verifying_key, key.signing_key


def load_pem_key_pair(public_key_pem, private_key_pem) -> 'tuple[PublicKeyTypes, PrivateKeyTypes]':
    public_key_loaded = serialization.load_pem_public_key(public_key_pem)
    private_key_loaded = serialization.load_pem_private_key(private_key_pem, password=None)
    return public_key_loaded, private_key_loaded


def dump_pem_key_pair(public_key, private_key):
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return public_key_pem, private_key_pem


def sign_rrset(rrset: 'RRset'):
    
    rdataclass = dns.rdataclass.RdataClass.IN
    rdatatype = dns.rdatatype.from_text(rrset.type)
    rdataset = dns.rdataset.Rdataset(rdclass=rdataclass, rdtype=rdatatype)

    records = rrset.records.all()
    for record in records:
        rdata = dns.rdata.from_text(rdclass=rdataclass, rdtype=rdatatype, tok=record.data)
        rdataset.add(rdata)

    