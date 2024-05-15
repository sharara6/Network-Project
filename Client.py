from socket import *
import os
import struct
import time
import matplotlib.pyplot as plt

# Constants
path1 = "C:\\Users\\AHMED\\Desktop\\New folder\\Network-Project\\medium file.jpeg"
mss = 8  # 64 bits = 8 bytes
HEADERSIZE = 1024
WINDOW_SIZE = 4
TIMEOUT = 1  # seconds

def create_packet(packet_id, file_id, data, trailer):
        return struct.pack('!HH8sI', packet_id, file_id, data, trailer)
    

def create_ack(packet_id, file_id):
        return struct.pack('!HH', packet_id, file_id)
    

def print_ack_received(packet_id):
    print(f"ACK received for packet number: {packet_id}")

def send_image(client, server_address):

    with open(path1, 'rb') as image:
        image_size = os.path.getsize(path1)
        size_info = f'{image_size:<{HEADERSIZE - len(str(HEADERSIZE))}}'.encode()
        client.sendto(size_info, server_address)
        print(f"Sent image size: {image_size}")
        file_data = image.read()
    
    packets = []
    file_id = 0
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
        if packet:
            packets.append(packet)
        packet_id += 1
        offset += mss
    
    base = 0
    next_seq_num = 0
    retransmissions = 0

    sent_packets = []
    send_times = []
    retransmitted_packets = []

    transfer_start_time = time.time()
    total_packets = len(packets)
    total_bytes = image_size

    while base < len(packets):
        while next_seq_num < base + WINDOW_SIZE and next_seq_num < len(packets):
            client.sendto(packets[next_seq_num], server_address)
            sent_packets.append(next_seq_num % 65536)
            send_times.append(time.time())
            print(f"Sent packet {next_seq_num % 65536} of file {file_id}")
            next_seq_num += 1
        
        start_time = time.time()
        
        while True:
            try:
                client.settimeout(TIMEOUT - (time.time() - start_time))
                ack_data, _ = client.recvfrom(8)  # 2 bytes packet_id + 2 bytes file_id
                ack_packet_id, ack_file_id = struct.unpack('!HH', ack_data)
                print_ack_received(ack_packet_id)
                
                if ack_packet_id >= base:
                    base = ack_packet_id + 1
                    break
            except timeout:
                print("Timeout occurred. Resending window from packet", base)
                retransmissions += 1
                next_seq_num = base  # Resend window
                retransmitted_packets.append(base)
                break

    transfer_end_time = time.time()
    elapsed_time = transfer_end_time - transfer_start_time

    plt.figure(figsize=(10, 6))
    plt.scatter(send_times, sent_packets, c='blue', label='Sent packets')
    plt.scatter([send_times[i] for i in retransmitted_packets], [sent_packets[i] for i in retransmitted_packets], c='red', label='Retransmitted packets')
    plt.xlabel('Time (s)')
    plt.ylabel('Packet ID')
    plt.title(f'Sent Packet IDs over Time\nWindow size: {WINDOW_SIZE}, Timeout: {TIMEOUT}s, Retransmissions: {retransmissions}')
    plt.legend()
    plt.show()

    print(f"Start time: {time.ctime(transfer_start_time)}")
    print(f"End time: {time.ctime(transfer_end_time)}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Number of packets sent: {total_packets}")
    print(f"Number of bytes sent: {total_bytes}")
    print(f"Number of retransmissions: {retransmissions}")
    if elapsed_time > 0:
        print(f"Average transfer rate: {total_bytes / elapsed_time:.2f} bytes/sec, {total_packets / elapsed_time:.2f} packets/sec")
    else:
        print("Elapsed time is too small to calculate transfer rate.")

# Main
server_address = (gethostname(), 8888)
with socket(AF_INET, SOCK_DGRAM) as client:
    send_image(client,server_address)