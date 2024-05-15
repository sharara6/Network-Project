import os
import struct
import time
import matplotlib.pyplot as plt
from PIL import Image
import random
from socket import *

path_to_save = "C:\\Users\\AHMED\\Desktop\\New folder\\Network-Project\\New folder"
mss = 8
HEADERSIZE = 1024

def save_data_to_file(file_id, data):
        image_name = f'file_{file_id}.jpeg'
        image_path = os.path.join(path_to_save, image_name)
        with open(image_path, 'ab') as image:
            image.write(data.strip(b'\0'))  
        return image_path


def send_acknowledgment(server_socket, packet_id, file_id, client_address):
        #server_socket: el socket bta3 el UDP elly b ysen el data 
        acknowledgment = struct.pack('!HH', packet_id, file_id) #use struct.pack to create an ACK (!HH m3naha 16 bit kol wa7da 2 bytes ! means big edian)
        server_socket.sendto(acknowledgment, client_address)#bib3at lel client el ACK
        print(f"Sent ACK for packet {packet_id} of file {file_id}")

def open_image(image_path):
        img = Image.open(image_path)
        img.show()
        print(f"Opened image {image_path}")

def simulate_packet_loss():
    rand = random.random()
    return 0.05 <= rand <= 0.15

with socket(AF_INET, SOCK_DGRAM) as server:
        server.bind((gethostname(), 8888))
        expected_packet_id = 0
        file_data = b''
        file_id = -1
        num_packets_received = 0
        num_bytes_received = 0

        received_packets = []
        receive_times = []

        start_time = time.time()

        while True:
            packet, address = server.recvfrom(1024)
            current_time = time.time()
            if len(packet) == 16:
                if simulate_packet_loss():
                    print("Simulated packet loss.")
                    continue

                try:
                    packet_id, file_id, data, trailer = struct.unpack('!HH8sI', packet)
                    print(f"Received packet {packet_id} for file {file_id}")
                except struct.error as e:
                    print(f"Error unpacking packet: {e}")
                    continue

                received_packets.append(packet_id)
                receive_times.append(current_time)

                if packet_id == expected_packet_id:
                    file_data += data
                    num_packets_received += 1
                    num_bytes_received += len(data)
                    if trailer == 0xFFFFFFFF:
                        image_path = save_data_to_file(file_id, file_data)
                        if image_path:
                            open_image(image_path)
                            end_time = time.time()
                            elapsed_time = end_time - start_time
                            print(f"File {file_id} saved successfully.")
                            print(f"Start time: {time.ctime(start_time)}")
                            print(f"End time: {time.ctime(end_time)}")
                            print(f"Elapsed time: {elapsed_time:.2f} seconds")
                            print(f"Number of packets received: {num_packets_received}")
                            print(f"Number of bytes received: {num_bytes_received}")
                            print(f"Average transfer rate: {num_bytes_received / elapsed_time:.2f} bytes/sec, {num_packets_received / elapsed_time:.2f} packets/sec")
                        file_data = b''
                        num_packets_received = 0
                        num_bytes_received = 0
                        start_time = current_time

                    expected_packet_id += 1
                    send_acknowledgment(server, packet_id, file_id, address)

                print(f"Expected next packet ID: {expected_packet_id}")
            elif len(packet) == 4:
                continue
            else:
                print(f"Received incorrect packet size: {len(packet)} bytes, expected 16 bytes or 4 bytes for ACK.")

        plt.figure(figsize=(10, 6))
        plt.scatter(receive_times, received_packets, c='blue', label='Received packets')
        plt.xlabel('Time (s)')
        plt.ylabel('Packet ID')
        plt.title(f'Received Packet IDs over Time')
        plt.legend()
        plt.show()
