import Pyro5.api
import Pyro5.core
from Pyro5.server import expose, oneway
import services.globalServices as gs
from models.interest import Interest
from models.ride import Ride

class ClientService(object):
    def __init__(self):
        self.ns = Pyro5.core.locate_ns()
        self.serverUri = self.ns.lookup("rideServer")
        self.uri = ''
        self.rideService = Pyro5.api.Proxy(self.serverUri)   
        self.notification_open = False
        self.rides = []
        self.interests = []
        self.keys = {'public': ..., 'private' : ...}

    @expose
    @oneway
    def notify_ride_available(self, name, phone, origin, destination, date):
        self.notification_open = True
        
        print('Someone offered a ride that you are interested! Get in touch and plan your trip!\n')
        print('Trip information: From: {0} || To: {1} || Date: {2} ({3} : {4})'.format(origin, destination, date, name, phone))
        self.exec_return()

    @expose
    @oneway
    def notify_passenger_interested(self, name, phone, origin, destination, date):
        self.notification_open = True
        
        print('Someone is interested in one of your rides! Get in touch and plan your trip!\n')
        print('Trip information: From: {0} || To: {1} || Date: {2} ({3} : {4})'.format(origin, destination, date, name, phone))
        self.exec_return()

    def exec_find_ride(self):
        
        origin = input("What's the origin of yout trip: ")
        destination = input("What's the destination of yout trip: ")
        date = input("What's the date of your trip (dd/mm/yyyy): ")
        notify = input('Do you want to get notified when someone offers a ride to {0}? (y/n): '.format(destination))
        notify = True if notify == 'y' else False

        interestData = bytes(str(self.uri if notify else None) + ';' + origin + ';' + destination + ';' + date, 'utf-8')
        
        signature = gs.setSignature(self.keys['private'], interestData)
        
        interest_id = self.rideService.registerInterest(self.uri if notify else None, origin, destination, date, signature)
        
        self.interests.append(Interest(interest_id, self.uri, origin, destination, date))

        rides = self.rideService.listRides(origin, destination, date)

        if(len(rides) > 0):
            print('\nThe following rides were found:\n')
            for ride in rides:
                print('From: {0} || To: {1} || Date: {2} ({3} : {4})'
                        .format(ride['origin'], ride['destination'], ride['date'], ride['userName'], ride['userPhone']))
        else:
            print("\nNo rides from {0} to {1} were found on this date.\n".format(origin, destination))
        self.exec_return()

    def exec_register_ride(self):
        
        origin = input('From where are you leaving: ')
        destination = input("Where are you going to: ")
        passengers = input("How many passengers are going: ")
        date = input("What's the date of your trip (dd/mm/yyyy): ")
        notify = input('Do you want to get notified when someone could be interested in your ride? (y/n): ')
        notify = True if notify == 'y' else False

        interestData = bytes(str(self.uri if notify else None) + ';' + origin + ';' + destination + ';' + date, 'utf-8')
        
        signature = gs.setSignature(self.keys['private'], interestData)

        ride_id = self.rideService.registerRide(self.uri if notify else None, origin, destination, passengers, date, signature)
        self.rides.append(Ride(ride_id, self.uri, origin, destination, date, passengers))
        print('\nYour trip was registered.')
        self.exec_return()

    def exec_cancel_interest(self):
        
        if(len(self.interests) > 0):
            print('Your ride interests:\n')
            for interest in self.interests:
                print('Id: {0} || From: {1} || To: {2} || Date: {3}'.format(interest.id, interest.origin, interest.destination, interest.date))

            interestId = int(input('\nEnter the interest id that you want to cancel: '))
            if(self.rideService.cancelInterest(interestId)):
                for interest in self.interests:
                    if interest.id == interestId:
                        self.interests.remove(interest)
        else:
            print("You don't have any ride interests.")
        self.exec_return()

    def exec_cancel_ride(self):
        
        if(len(self.rides) > 0):
            print('Your rides:\n')
            for ride in self.rides:
                print('Id: {0} || From: {1} || To: {2} || Passengers: {3} || Date: {4}'.format(ride.id, ride.origin, ride.destination, ride.seats, ride.date))
                
            rideId = int(input('\nEnter the Id of the ride that you want to cancel: '))
            if(self.rideService.cancelRide(rideId)):
                for ride in self.rides:
                    if ride.id == rideId:
                        self.rides.remove(ride)
        else:
            print("You don't have any rides scheduled.")
        self.exec_return()

    def exec_return(self):
        option = 0
        print('\nX - Return\n\n> ', end='')
        while(option != 'X'):
            option = input()
            if(option == 'X' or option == 'x'):
                option = 0
                break

    def exec_menu(self):
        
        self.name = input("What is your name? ").strip()
        self.phone = input("And your phone number? ").strip()
        
        self.keys = gs.generateKeys()
        
        publicPem = gs.generatePem(self.keys['public'])

        if(not self.rideService.registerUser(self.name, self.phone, publicPem)):
            print("\nThe informed phone is already in use. Exiting...\n")
        else:
            option = 0
            switchCase = {
                            1: self.exec_find_ride,
                            2: self.exec_register_ride,
                            3: self.exec_cancel_interest,
                            4: self.exec_cancel_ride
                        }

            while(option >= 0):
                gs.printOptions()
                option = gs.checkValidOption(option)

                if(option == 'x'):
                    if(not self.notification_open):
                        print('X')
                        break
                    else:
                        self.notification_open = False
                else:
                    gs.switch(option, switchCase)()

                option = 0

