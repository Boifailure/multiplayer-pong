from enum import IntEnum
from struct import pack, unpack

"""
Message bytes:
-byte 1: type of message
-byte 2-3 (for simple type only): message id
-byte 2-3 (for join type only): port
-rest (optional): data (dataBytes)
"""

class MessageType(IntEnum):
    Simple = 0
    Join = 1
    Welcome = 2
    Leave = 3

class Message:
    def __init__(self, messageType : MessageType = MessageType.Simple, id : int = 0):
        self.dataBytes : bytearray = bytearray()
        self.messageType : int = messageType
        self.id : int = id
    
    def __str__(self):
        return f"Message ({self.dataBytes})"

    @staticmethod
    def Deserialize(data : bytearray):
        message : Message = Message()
        message.dataBytes = data

        message.messageType = message.GetByte()
        if message.messageType == MessageType.Simple:
            message.id = message.GetUInt16()
        
        return message
    
    def Serialize(self) -> bytearray:
        data = bytearray()
        data += bytearray([self.messageType])
        if self.messageType == MessageType.Simple:
            data += bytearray(self.id.to_bytes(2, signed=False))
        data += self.dataBytes
        return data
    
    def AddByte(self, data : int):
        self.AddByteArray(bytearray([data]))
    def AddByteArray(self, data : bytearray):
        self.dataBytes += data
    def AddBytes(self, data : bytes):
        self.AddByteArray(bytearray(data))
    def AddInt32(self, data : int):
        self.AddBytes(data.to_bytes(4, signed=True))
    def AddUInt32(self, data : int):
        self.AddBytes(data.to_bytes(4, signed=False))
    def AddInt16(self, data : int):
        self.AddBytes(data.to_bytes(2, signed=True))
    def AddUInt16(self, data : int):
        self.AddBytes(data.to_bytes(2, signed=False))
    def AddBool(self, data : bool):
        self.AddByteArray(bytearray([0xFF if data else 0x00]))
    def AddFloat(self, data : float):
        self.AddBytes(pack("<f", data))
    
    def GetByte(self) -> int:
        return self.dataBytes.pop(0)
    def GetByteArray(self, length : int) -> bytearray:
        data = self.dataBytes[:length]
        del self.dataBytes[:length]
        return data
    def GetInt32(self) -> int:
        return int.from_bytes(self.GetByteArray(4), signed=True)
    def GetUInt32(self) -> int:
        return int.from_bytes(self.GetByteArray(4), signed=False)
    def GetInt16(self) -> int:
        return int.from_bytes(self.GetByteArray(2), signed=True)
    def GetUInt16(self) -> int:
        return int.from_bytes(self.GetByteArray(2), signed=False)
    def GetBool(self):
        return self.GetByte() != 0
    def GetFloat(self):
        return unpack("<f", self.GetByteArray(4))[0]