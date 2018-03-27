import socket
import sys

host = '10.97.165.175'
port = 123
addr = (host, port)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = str.encode("something")
udp_socket.sendto(data, addr)
res, addr = udp_socket.recvfrom(1024)
print(bytes.decode(res))


udp_socket.close()
