import Pyro5.api
import Pyro5.core
import threading
from Pyro5.server import expose, oneway
from services.clientService import ClientService

class ClientDaemon(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.setDaemon(True)
        
    def run(self):
        with Pyro5.server.Daemon() as daemon:
            self.client.uri = daemon.register(self.client)
            daemon.requestLoop()

client = ClientService()

client_daemon = ClientDaemon(client)
client_daemon.start()


client.exec_menu()