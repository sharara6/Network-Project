from socket import*


with socket(AF_INET, SOCK_DGRAM) as client:
    message = input("Type your Message")
    client.sendto(message.encode(), (gethostname(), 8888))
    newMessage, adr = client.recvfrom(1024)
    print(newMessage.decode())
    client.close()