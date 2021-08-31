from inspect import signature
from cryptography.hazmat.primitives.serialization import base
from unique_id import get_unique_id
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from random import seed, randint
import Pyro5.api
import Pyro5.core

def getPubKeyFromPem(pem):
    pem_data = base64.b64decode(pem["data"])
    return serialization.load_pem_public_key(pem_data)

def getSpecificRides(registered_rides, origin, destination, date):
    found_rides = []

    if(len(registered_rides) > 0):
        for ride in registered_rides:
            if(ride.origin == origin and ride.destination == destination and ride.date == date):
                found_rides.append(ride)
    
    return found_rides

def getFirstSpecificInterest(registered_interests, origin, destination, date):
    for interest in registered_interests:
        if(interest.origin == origin and interest.destination == destination and interest.date == date):
            return interest.userUri
    return None

def generateKeys():
        keys = {'private': None, 'public': None}
        keys['private'] = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        keys['public'] = keys['private'].public_key()
        return keys

def generatePem(publicKey):
    return publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)

def setSignature(privateKey, interestData):
    return privateKey.sign(interestData,
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256())

def getSignature(encSignature):
    return base64.b64decode(encSignature['data'])

def verifySignature(publicKey, signature, interestData):
    try:
        publicKey.verify(
                    signature,
                    interestData,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def printOptions():
    print('Choose one of the following:')
    print('\n')
    print('1 - Find a ride.')
    print('2 - Offer a ride.')
    print('3 - Cancel an interest.')
    print('4 - Cancel a ride.')
    print('X - Exit.')
    print('\n')

def checkValidOption(op):
    option = op
    while(option != 'x' and (option < 1 or option > 4)):
        print('\r> ', end='')
        option = input()
        try:
            option = int(option)
        except:
            option = -1 if option != 'X' and option != 'x' else 'x'
    return option

def switch(op, _switchCase):
    print(op)
    return _switchCase.get(op)

def getUserObject(user_uri):
        return Pyro5.api.Proxy(user_uri)

        

