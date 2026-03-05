from networking.message import Message, MessageType
from networking.udp_transport import UDPTransport

class Client:
    def __init__(self, ip : str, port : int, incomingPort : None | int = None):
        self.serverAddress = (ip, port)
        self.transport = UDPTransport(("0.0.0.0", incomingPort))

        self.messageIDCallbacks = {}
        self.onJoin = None
        self.onLeft = None

        if incomingPort == None:
            incomingPort = port
        joinMessage = Message(MessageType.Join)
        joinMessage.AddUInt16(incomingPort)
        self.Send(joinMessage)

        self.connected : bool = False
        
    def Send(self, message : Message) -> bool:
        if not self.transport.send(message.Serialize(), self.serverAddress):
            if self.onLeft:
                self.onLeft()
            self.transport.close()
            self.connected = False
            return False
        return True
        
    def Update(self):
        newPackets = self.transport.receive_all()

        for packet, ip in newPackets:
            message = Message.Deserialize(bytearray(packet))

            match message.messageType:

                case MessageType.Simple:
                    self.messageIDCallbacks[message.id](message)

                case MessageType.Welcome:
                    if self.onJoin:
                        self.onJoin()
                    self.connected = True

                case MessageType.Leave:
                    if self.onLeft:
                        self.onLeft()
                    self.transport.close()
                    self.connected = False

    def RegisterMessageID(self, messageID : int, callback):
        self.messageIDCallbacks[messageID] = callback
    
    def Leave(self):
        self.Send(Message(MessageType.Leave))
        if self.onLeft:
            self.onLeft()
        self.transport.close()
        self.connected = False