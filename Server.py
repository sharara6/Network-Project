from socket import *
import os

path_to_save = 'C:\\Users\\AHMED\\Desktop\\New folder (2)\\Network-Project\\received_images\\'
mss = 1024
HEADERSIZE = 1024

# Server side
with socket(AF_INET, SOCK_DGRAM) as server:
    server.bind((gethostname(), 8888))
    
    while True:
        packet_id, address = server.recvfrom(2048)  # Adjust buffer size to match packet size
        packet_id = int(packet_id.decode())
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
