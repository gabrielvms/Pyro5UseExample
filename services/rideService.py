import Pyro5.api
import Pyro5.nameserver
from models.user import User
from models.ride import Ride
from models.interest import Interest
import services.globalServices as gs


registered_users = []
registered_rides = []
registered_interests = []
rideId = 1000
interestId = 1000

@Pyro5.api.expose
class RideService(object):
    def registerUser(self, name, phone, pem):

        publicKey = gs.getPubKeyFromPem(pem)

        self.user = User(name, phone, publicKey)
        if(any(x.phone == phone for x in registered_users)):
            print('The user already exist.')
            return False
        else:
            registered_users.append(self.user)
            print('User registration is done.')
            return True
    
    def listRides(self, origin, destination, date):
        found_rides = gs.getSpecificRides(registered_rides, origin, destination, date)

        for ride in found_rides:
            if(ride['userUri'] != None):
                rideUserClient = gs.getUserObject(ride['userUri']) #client dono da corrida
                rideUserClient.notify_passenger_interested(self.user.name, self.user.phone, #dono da corrida recebe a notificacao de interesse
                                                     ride['origin'], ride['destination'], ride['date']) 
        
        return found_rides



    def registerInterest(self, uri, origin, destination, date, encSignature):
        signature = gs.getSignature(encSignature)
        interestData = bytes(str(uri if uri != None else None) + ';' + origin + ';' + destination + ';' + date, 'utf-8')
        isSignatureValid = gs.verifySignature(self.user.publicKey, signature, interestData)

        if(isSignatureValid):
            self.user.uri = uri
            global interestId
            id = interestId
            interestId += 1
            registered_interests.append(Interest(id, self.user, origin, destination, date))
            print('The interest {0} was successfully registered.'.format(id))
            return id
        else:
            print("The signature is Invalid!")

    def registerRide(self, uri, origin, destination, passengers, date, encSignature):
        signature = gs.getSignature(encSignature)
        interestData = bytes(str(uri if uri != None else None) + ';' + origin + ';' + destination + ';' + date, 'utf-8')
        isSignatureValid = gs.verifySignature(self.user.publicKey, signature, interestData)
        
        if(isSignatureValid):
            self.user.uri = uri
            global rideId
            id = rideId
            rideId += 1
            registered_rides.append(Ride(id, self.user, origin, destination, date, passengers))
            
            remoteUserUri = gs.getFirstSpecificInterest(registered_interests, origin, destination, date)
            if(remoteUserUri != None):
                remoteUser = gs.getUserObject(remoteUserUri)
                remoteUser.notify_rideAvailable(self.user.name, self.user.phone, origin, destination, date)
            print('The ride {0} was successfully registered.'.format(id))
            return id
        else:
            print("The signature is Invalid!")

    def cancelInterest(self, interestId):
        for interest in registered_interests:
            if interest.id == interestId:
                registered_interests.remove(interest)
                print('The interest {0} was successfully cancelled.'.format(interestId))
                return True
        return False

    def cancelRide(self, rideId):
        for ride in registered_rides:
            if ride.id == rideId:
                registered_rides.remove(ride)
                print('The ride {0} was successfully cancelled.'.format(rideId))
                return True
        return False
            