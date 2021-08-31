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

        # rides = self.rideService.listRides(origin, destination, date)

        # if(len(rides) > 0):
        #     print('\nThe following rides were found:\n')
        #     for ride in rides:
        #         rideUser = gs.getUserObject(ride.userUri)
        #         print('From: {0} || To: {1} || Date: {2} ({3} : {4})'
        #                 .format(ride.origin, ride.destination, ride.date, rideUser.name,rideUser.phone))
        # else:
        #     print("\nNo rides from {0} to {1} were found on this date.\n".format(origin, destination))
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
        self.rides.append([ride_id, origin, destination, passengers, date])
        print('\nYour trip was registered.')
        self.exec_return()

    def exec_cancel_interest(self):
        
        if(len(self.interests) > 0):
            print('Your ride interests:\n')
            idx = 0
            for interest in self.interests:
                print('{0} - Id: {1} || From: {2} || To: {3} || Date: {4}'.format(idx, interest[0], interest[1], interest[2], interest[3]))
                idx = idx + 1
            interest_idx = int(input('\nType the interest number that you want to cancel: '))
            if(self.ride_service.cancel_interest(self.interests[interest_idx][0])):
                self.interests.pop(interest_idx)
        else:
            print("You don't have any ride interests.")
        self.exec_return()

    def exec_cancel_ride(self):
        
        if(len(self.rides) > 0):
            print('Your rides:\n')
            idx = 0
            for ride in self.rides:
                print('{0} - Id: {1} || From: {1} || To: {2} || Passengers: {3} || Date: {4}'.format(idx, ride[0], ride[1], ride[2], ride[3], ride[4]))
                idx = idx + 1
            ride_idx = int(input('\nType the ride number that you want to cancel: '))
            if(self.ride_service.cancel_ride(self.rides[ride_idx][0])):
                self.rides.pop(ride_idx)
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
        
        pem = gs.generatePem(self.keys['public'])

        if(not self.rideService.registerUser(self.name, self.phone, pem)):
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

