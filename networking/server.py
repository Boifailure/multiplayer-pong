from networking.message import Message, MessageType
from networking.udp_transport import UDPTransport

class Client:
    def __init__(self, ip : str, port : int, id : int, parentServer):
        self.ip : str = ip
        self.port : int = port
        self.id : int = id
        self.parentServer = parentServer

    def Disconnect(self):
        self.parentServer.Send(Message(MessageType.Leave), self)
        if self.parentServer.onClientLeave:
            self.parentServer.onClientLeave(self)
        self.parentServer.clients.pop(self.id)

    def __str__(self):
        return f"(ID: {self.id}, IP: {self.ip}, Port: {self.port})"

class Server:
    def __init__(self, port : int, maxClientCount : int = 16, logMessages : bool = False):
        self.port : UDPTransport = port
        self.transport : UDPTransport = UDPTransport(("0.0.0.0", port))
        self.clients : dict[int, Client] = {}
        self.maxClientCount : int = maxClientCount

        self.messageIDCallbacks = {}
        self.onClientJoin = None
        self.onClientLeave = None

        self.logMessages : bool = logMessages

    def Send(self, message : Message, client : Client) -> bool:
        if not self.transport.send(message.Serialize(), (client.ip, client.port)):
            if self.onClientLeave:
                self.onClientLeave(client)
            self.clients.pop(client.id)
            return False
        return True

    def SendToAll(self, message : Message):
        for clientID, client in self.clients.items():
            self.Send(message, client)
    
    def Update(self):
        newPackets = self.transport.receive_all()

        for packet, ip in newPackets:
            message = Message.Deserialize(bytearray(packet))
            client = self._GetClientByIp(ip)

            if self.logMessages:
                print(str(message))

            match message.messageType:

                case MessageType.Simple:
                    if client == None:
                        break
                    self.messageIDCallbacks[message.id](self._GetClientByIp(ip).id, message)

                case MessageType.Join:
                    if len(self.clients) >= self.maxClientCount:
                        break
                    client = Client(ip, message.GetUInt16(), self._NextAvailablePlayerID(), self)
                    self.clients[client.id] = client
                    self.Send(Message(MessageType.Welcome), client)
                    if self.onClientJoin:
                        self.onClientJoin(client)

                case MessageType.Leave:
                    if client == None:
                        break
                    if self.onClientLeave:
                        self.onClientLeave(client)
                    self.clients.pop(client.id)
    
    def RegisterMessageID(self, messageID : int, callback):
        self.messageIDCallbacks[messageID] = callback
    
    def _NextAvailablePlayerID(self) -> int:
        i = 0
        while i in self.clients:
            i += 1
        return i
    
    def _GetClientByIp(self, ip : str) -> None | Client:
        for clientID, client in self.clients.items():
            if client.ip == ip:
                return client
        return None