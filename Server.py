from socket import *
import os
import struct

path_to_save = "C:\\Users\\Blu-Ray\\OneDrive\\Pictures\\network_recieved_images"
mss = 32
HEADERSIZE = 1024

def save_data_to_file(file_id, data):
    image_name = f'file_{file_id}.jpeg'
    image_path = os.path.join(path_to_save, image_name)
    with open(image_path, 'ab') as image:
        image.write(data.strip(b'\0'))  # Strip null padding if present

def send_acknowledgment(server_socket, packet_id, file_id, client_address):
    acknowledgment = struct.pack('!HH', packet_id, file_id)
    server_socket.sendto(acknowledgment, client_address)

# Server side
with socket(AF_INET, SOCK_DGRAM) as server:
    server.bind((gethostname(), 8888))
    expected_packet_id = 0
    file_data = b''

    while True:
        packet, address = server.recvfrom(2048)  # Adjust buffer size to accommodate the entire packet
        if len(packet) != 40:
            print(f"Received incorrect packet size: {len(packet)} bytes, expected 40 bytes.")
            continue  # Skip processing this packet
        
        packet_id, file_id, data, trailer = struct.unpack('!HH32sI', packet)
        
        if packet_id == expected_packet_id:
            file_data += data
            if trailer == 0xFFFFFFFF:  # Last packet
                save_data_to_file(file_id, file_data)
                print(f"File {file_id} saved successfully.")
                file_data = b''  # Reset for next file
            expected_packet_id += 1
        
        # Send acknowledgment for the last received in-order packet
        send_acknowledgment(server, packet_id, file_id, address)
        
        print(f"Received packet {packet_id} for file {file_id}")
        print(f"Expected next packet ID: {expected_packet_id}")
