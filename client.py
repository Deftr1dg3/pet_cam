#!/usr/bin/env python3

import cv2
import numpy as np
import socket
import struct

# Create a socket for sending data
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.3', 8888))

# Create a video capture object
cap = cv2.VideoCapture(0)

# Get the video frame width and height
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create a video writer object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (frame_width, frame_height))

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Encode the frame as a JPEG image
    data = cv2.imencode('.jpg', frame)[1].tostring()

    # Send the data to the remote machine
    client_socket.sendall(struct.pack('<L', len(data)) + data)

    # Display the frame on the local machine
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and writer objects
cap.release()
out.release()

# Close the socket and destroy the window
client_socket.close()
cv2.destroyAllWindows()