from socket import *
import os
import struct
import time
import matplotlib.pyplot as plt
from PIL import Image

path_to_save = "C:\\Users\\AHMED\\Desktop\\New folder\\Network-Project\\New folder"
mss = 8 
HEADERSIZE = 1024

def save_data_to_file(file_id, data):#Taha #################################################################
    image_name = f'file_{file_id}.jpeg'
    image_path = os.path.join(path_to_save, image_name)
    with open(image_path, 'ab') as image:
        image.write(data.strip(b'\0'))  # Strip null padding if present
    return image_path

def send_acknowledgment(server_socket, packet_id, file_id, client_address):
    #server_socket = el UDP socket elly b nrecieve packet 3alih

    acknowledgment = struct.pack('!HH', packet_id, file_id)
    server_socket.sendto(acknowledgment, client_address)
    print(f"Sent ACK for packet {packet_id} of file {file_id}")

def open_image(image_path):
    try:
        img = Image.open(image_path)
        img.show()
        print(f"Opened image {image_path}")
    except Exception as e:
        print(f"Failed to open image {image_path}: {e}")


# Server side
with socket(AF_INET, SOCK_DGRAM) as server:
    server.bind((gethostname(), 8888))
    expected_packet_id = 0
    file_data = b''
    file_id = -1
    num_packets_received = 0
    num_bytes_received = 0

    # Data for plotting
    received_packets = []
    receive_times = []

    start_time = time.time()

    while True:
        packet, address = server.recvfrom(1024)
        current_time = time.time()
        if len(packet) == 16:  # Check if it's a data packet
            packet_id, file_id, data, trailer = struct.unpack('!HH8sI', packet)
            print(f"Received packet {packet_id} for file {file_id}")

            received_packets.append(packet_id)
            receive_times.append(current_time)

            if packet_id == expected_packet_id:
                file_data += data
                num_packets_received += 1
                num_bytes_received += len(data)
                if trailer == 0xFFFFFFFF:  # Last packet
                    image_path = save_data_to_file(file_id, file_data)
                    open_image(image_path)  # Open the image once saved
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"File {file_id} saved successfully.")
                    print(f"Start time: {time.ctime(start_time)}")
                    print(f"End time: {time.ctime(end_time)}")
                    print(f"Elapsed time: {elapsed_time:.2f} seconds")
                    print(f"Number of packets received: {num_packets_received}")
                    print(f"Number of bytes received: {num_bytes_received}")
                    print(f"Average transfer rate: {num_bytes_received / elapsed_time:.2f} bytes/sec, {num_packets_received / elapsed_time:.2f} packets/sec")
                    file_data = b''  # Reset for next file
                    num_packets_received = 0
                    num_bytes_received = 0
                    start_time = current_time  # Reset start time for next file
                expected_packet_id += 1

            # Send acknowledgment for the last received in-order packet
            send_acknowledgment(server, packet_id, file_id, address)

            print(f"Expected next packet ID: {expected_packet_id}")
        elif len(packet) == 4:  # Check if it's an acknowledgment packet
            continue
        else:
            print(f"Received incorrect packet size: {len(packet)} bytes, expected 16 bytes or 4 bytes for ACK.")

    # Plot the received packets
    plt.figure(figsize=(10, 6))
    plt.scatter(receive_times, received_packets, c='blue', label='Received packets')
    plt.xlabel('Time (s)')
    plt.ylabel('Packet ID')
    plt.title(f'Received Packet IDs over Time')
    plt.legend()
    plt.show()
