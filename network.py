import socket
import pickle


class Network:
    def __init__(self, name):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.105"
        self.port = 5050
        self.addr = (self.server, self.port)
        self.p = self.connect(name) #มีnameในวงเล็บ

    def getP(self):
        return self.p

    def connect(self, name):
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode(name))
            return pickle.loads(self.client.recv(2048*2)) #แค่connectก็โหลดnameแล้ว
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048*2))
        except socket.error as e:
            return {}
    
    def oneway_send(self, data): #send แล้วไม่load
        try:
            self.client.send(str.encode(data))
        except socket.error as e:
            print(e)

