from socket import *
import os
import struct
import random

path_to_save = "C:\\Users\\AHMED\\Desktop\\New folder\\Network-Project\\New folder"
mss = 8  # 64 bits = 8 bytes
HEADERSIZE = 1024

# Simulated packet loss rate (5% to 15%)
PACKET_LOSS_RATE = random.uniform(0.05, 0.15)


def save_data_to_file(file_id, data):
    image_name = f'file_{file_id}.jpeg'
    image_path = os.path.join(path_to_save, image_name)
    with open(image_path, 'ab') as image:
        image.write(data.strip(b'\0'))  # Strip null padding if present


def send_acknowledgment(server_socket, packet_id, file_id, client_address):
    acknowledgment = struct.pack('!HH', packet_id, file_id)
    server_socket.sendto(acknowledgment, client_address)
    print(f"Sent ACK for packet {packet_id} of file {file_id}")


def simulate_packet_loss():
    return random.random() < PACKET_LOSS_RATE


# Server side
with socket(AF_INET, SOCK_DGRAM) as server:
    server.bind((gethostname(), 8888))
    expected_packet_id = 0
    file_data = b''

    while True:
        # Adjust buffer size to accommodate the entire packet
        packet, address = server.recvfrom(1024)
        if len(packet) == 16:  # Check if it's a data packet
            if simulate_packet_loss():
                print("Simulated packet loss.")
                continue  # Skip processing this packet to simulate loss

            packet_id, file_id, data, trailer = struct.unpack('!HH8sI', packet)
            print(f"Received packet {packet_id} for file {file_id}")

            if packet_id == expected_packet_id:
                file_data += data
                if trailer == 0xFFFFFFFF:  # Last packet
                    save_data_to_file(file_id, file_data)
                    print(f"File {file_id} saved successfully.")
                    file_data = b''  # Reset for next file
                expected_packet_id += 1

            # Send acknowledgment for the last received in-order packet
            send_acknowledgment(server, packet_id, file_id, address)

            print(f"Expected next packet ID: {expected_packet_id}")
        elif len(packet) == 4:  # Check if it's an acknowledgment packet
            # Handle acknowledgment packets if needed
            continue
        else:
            print(
                f"Received incorrect packet size: {len(packet)} bytes, expected 16 bytes or 4 bytes for ACK.")
