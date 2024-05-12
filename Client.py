from socket import *
import os

path1 = "C:\\Users\\AHMED\\Desktop\\New folder (2)\\Network-Project\\small file.jpeg"
mss = 200
HEADERSIZE = 2048

def send_packet(packet_id, file_id, data, trailer):
    client.sendto(f'{packet_id:<16}'.encode() + f'{file_id:<16}'.encode() + data + trailer, (gethostname(), 8888))

# Open the image file
with open(path1, 'rb') as image:
    image_size = os.path.getsize(path1)

    with socket(AF_INET, SOCK_DGRAM) as client:
        # Send the image size
        client.sendto(f'{image_size:<{HEADERSIZE - len(str(HEADERSIZE))}}'.encode(), (gethostname(), 8888))
        
        # Send the image data in chunks
        file_id = 0
        packet_id = 0
        while True:
            # Read a chunk of data from the image file
            data = image.read(mss)
            if not data:
                break
            
            # Send the data in chunks of size mss
            offset = 0
            while offset < len(data):
                chunk = data[offset:offset+mss]
                send_packet(packet_id, file_id, chunk, b'\x00\x00\x00\x00')  # Trailer set to 0x0000
                offset += mss
            
            # Increment packet_id
            packet_id += 1

        # Send the last packet with the trailer set to 0xFFFF
        send_packet(packet_id, file_id, b'', b'\xFF\xFF\x00\x00')
