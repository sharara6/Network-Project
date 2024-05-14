from socket import *
import os
import struct
import time

# Constants
path1 = "C:\\Users\\AHMED\\Desktop\\New folder\\Network-Project\\medium file.jpeg"
mss = 8  # 64 bits = 8 bytes
HEADERSIZE = 1024
WINDOW_SIZE = 4
TIMEOUT = 2  # seconds


def create_packet(packet_id, file_id, data, trailer):
    return struct.pack('!HH8sI', packet_id, file_id, data, trailer)


def create_ack(packet_id, file_id):
    return struct.pack('!HH', packet_id, file_id)


def print_ack_received(packet_id):
    print(f"ACK received for packet number: {packet_id}")


def send_image(client, server_address):
    with open(path1, 'rb') as image:
        image_size = os.path.getsize(path1)

        # Send the image size
        size_info = f'{image_size:<{HEADERSIZE - len(str(HEADERSIZE))}}'.encode()
        client.sendto(size_info, server_address)
        print(f"Sent image size: {image_size}")

        # Read the entire file into memory
        file_data = image.read()

    # Create packets
    packets = []
    file_id = 3
    packet_id = 0
    offset = 0
    while offset < len(file_data):
        chunk = file_data[offset:offset + mss]
        if len(chunk) < mss:
            chunk = chunk.ljust(mss, b'\0')
        trailer = 0x00000000
        if offset + mss >= len(file_data):
            trailer = 0xFFFFFFFF  # Last packet
        packet = create_packet(packet_id % 65536, file_id, chunk, trailer)
        packets.append(packet)
        packet_id += 1
        offset += mss

    # Go-Back-N Sliding Window
    base = 0
    next_seq_num = 0
    while base < len(packets):
        while next_seq_num < base + WINDOW_SIZE and next_seq_num < len(packets):
            client.sendto(packets[next_seq_num], server_address)
            print(f"Sent packet {next_seq_num % 65536} of file {file_id}")
            next_seq_num += 1

        # Start the timer
        start_time = time.time()

        while True:
            try:
                client.settimeout(TIMEOUT - (time.time() - start_time))
                # 2 bytes packet_id + 2 bytes file_id
                ack_data, _ = client.recvfrom(8)
                ack_packet_id, ack_file_id = struct.unpack('!HH', ack_data)
                print_ack_received(ack_packet_id)

                if ack_packet_id >= base:
                    base = ack_packet_id + 1
                    break
            except timeout:
                print("Timeout occurred. Resending window from packet", base)
                next_seq_num = base  # Resend window
                break


# Main
server_address = (gethostname(), 8888)
with socket(AF_INET, SOCK_DGRAM) as client:
    send_image(client, server_address)
