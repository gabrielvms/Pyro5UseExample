import Pyro5.api
import Pyro5.nameserver
import threading
from services.rideService import RideService

class NameServer(threading.Thread):
    def run(self):
        Pyro5.nameserver.start_ns_loop()

nameserver = NameServer()
nameserver.start()

daemon = Pyro5.server.Daemon()              
ns = Pyro5.api.locate_ns()                 
uri = daemon.register(RideService)  
ns.register("rideServer", uri)          

print("Server is Ready.")
daemon.requestLoop()                        