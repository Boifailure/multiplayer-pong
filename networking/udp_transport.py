import socket

class UDPTransport:
    def __init__(self, localAddress: tuple[str, int] = ("0.0.0.0", 8888), bufferSize : int = 65535, disposePreviousPackets : bool = True):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(localAddress)
        self.socket.setblocking(False)
        self.bufferSize = bufferSize
        if disposePreviousPackets:
            self.receive_all()
        self.running = True

    def send(self, data: bytes, remote_addr: tuple[str, int]) -> bool:
        try:
            self.socket.sendto(data, remote_addr)
            return True
        except:
            return False

    def receive_all(self) -> list[tuple[bytes, str]]:
        """
        Returns all packets received since the last call.
        Each item is (data, sender_address).
        """
        packets = []

        while True:
            try:
                data, addr = self.socket.recvfrom(self.bufferSize)
                packets.append((data, addr[0]))
            except:
                break

        return packets

    def close(self):
        self.socket.close()
        self.running = False