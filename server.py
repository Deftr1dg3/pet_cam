#!/usr/bin/env python3

import cv2
import numpy as np
import socket
import struct


# Create a socket for receiving data
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.3', 12345))
server_socket.listen(0)

# Accept a connection from the sender
connection, address = server_socket.accept()

print(f'[INFO] Client connected => {address}')

while True:
    # Read the length of the data to be received
    data_length = struct.unpack('<L', connection.recv(4))[0]

    # Receive the data
    data = b''
    while len(data) < data_length:
        data += connection.recv(4096)

    # Decode the data and display the frame

    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), 1)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the connection and destroy the window
connection.close()
cv2.destroyAllWindows()