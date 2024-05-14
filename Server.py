from socket import *
import os

path_to_save = "C:\\Users\\Blu-Ray\\OneDrive\\Pictures\\network_recieved_images"
mss = 1024
HEADERSIZE = 1024

# Function to send acknowledgment
def send_acknowledgment(server_socket, packet_id, file_id, client_address):
    ack_packet_id = packet_id.to_bytes(2, byteorder='big')
    ack_file_id = file_id.to_bytes(2, byteorder='big')
    acknowledgment = ack_packet_id + ack_file_id
    server_socket.sendto(acknowledgment, client_address)

# Server side
with socket(AF_INET, SOCK_DGRAM) as server:
    server.bind((gethostname(), 8888))
    while True:
        # Receive the packet ID
        packet_id_bytes, address = server.recvfrom(2048)  # Adjust buffer size to match packet size
        packet_id = int(packet_id_bytes.decode())

        # Receive the file ID
        file_id_bytes, address = server.recvfrom(2048)  # Adjust buffer size to match packet size
        file_id = int.from_bytes(file_id_bytes, byteorder='big')
        print("Received packet:", packet_id, "for file ID:", file_id)

        # Receive data until the end of the file
        data = b''
        while True:
            chunk, address = server.recvfrom(mss)
            data += chunk
            if len(chunk) < mss:
                break

        # Write data to file
        image_name = f'file_{file_id}.jpeg'  # Adjust filename as needed
        image_path = os.path.join(path_to_save, image_name)
        with open(image_path, 'ab') as image:
            image.write(data)
        
        print("Packet", packet_id, "saved as:", image_path)

        # Send acknowledgment
        send_acknowledgment(server, packet_id, file_id, address)
