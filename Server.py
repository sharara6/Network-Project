HEADER = 32

import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((socket.gethostname(), 8888))
    while True:
        message, address = server.recvfrom(1024)
        newMessage = message.decode().upper()
        newMessageSize = len(newMessage)
        newMessage = f'{newMessageSize:<{HEADER - len(str(newMessageSize))}}{newMessage}'
        server.sendto(newMessage.encode(), address)
