from __future__ import print_function
import zmq
import threading
import numpy as np
import struct
import time
from datetime import datetime
import socket
import sys
import os
import yaml
import logging
from collections import deque
if sys.version_info < (3, 0):
    from subprocess32 import Popen, PIPE
else:
    from subprocess import Popen, PIPE


RPC_VERSION = 3

INPUT_TYPE_BYTES = 0
INPUT_TYPE_INTS = 1
INPUT_TYPE_FLOATS = 2
INPUT_TYPE_DOUBLES = 3
INPUT_TYPE_STRINGS = 4

REQUEST_TYPE_PREDICT = 0
REQUEST_TYPE_FEEDBACK = 1

MESSAGE_TYPE_NEW_CONTAINER = 0
MESSAGE_TYPE_CONTAINER_CONTENT = 1
MESSAGE_TYPE_HEARTBEAT = 2

HEARTBEAT_TYPE_KEEPALIVE = 0
HEARTBEAT_TYPE_REQUEST_CONTAINER_METADATA = 1

SOCKET_POLLING_TIMEOUT_MILLIS = 5000
SOCKET_ACTIVITY_TIMEOUT_MILLIS = 30000

EVENT_HISTORY_BUFFER_SIZE = 30

EVENT_HISTORY_SENT_HEARTBEAT = 1
EVENT_HISTORY_RECEIVED_HEARTBEAT = 2
EVENT_HISTORY_SENT_CONTAINER_METADATA = 3
EVENT_HISTORY_RECEIVED_CONTAINER_METADATA = 4
EVENT_HISTORY_SENT_CONTAINER_CONTENT = 5
EVENT_HISTORY_RECEIVED_CONTAINER_CONTENT = 6

MAXIMUM_UTF_8_CHAR_LENGTH_BYTES = 4
BYTES_PER_LONG = 8

# Initial size of the buffer used for receiving
# request input content
INITIAL_INPUT_CONTENT_BUFFER_SIZE = 1024
# Initial size of the buffers used for sending response
# header data and receiving request header data
INITIAL_HEADER_BUFFER_SIZE = 1024

INPUT_HEADER_DTYPE = np.dtype(np.uint64)

# host_name = socket.gethostname()
# print(host_name)
host_ip = '127.0.0.1'
# socket.gethostbyname(host_name)
print(host_ip)
sys.stdout.flush()
sys.stderr.flush()
port = 7999


def validate_rpc_version(received_version):
        if received_version != RPC_VERSION:
            print(
                "ERROR: Received an RPC message with version: {clv} that does not match container version: {mcv}"
                .format(clv=received_version, mcv=RPC_VERSION))

def send_heartbeat(socket):

        if sys.version_info < (3, 0):
            socket.send("", zmq.SNDMORE)
        else:
            socket.send_string("", zmq.SNDMORE)
        socket.send(struct.pack("<I", RPC_VERSION))
        socket.send(struct.pack("<I", MESSAGE_TYPE_HEARTBEAT))
        socket.send(struct.pack("<I",HEARTBEAT_TYPE_KEEPALIVE))

        # self.event_history.insert(EVENT_HISTORY_SENT_HEARTBEAT)
        print("Sent heartbeat!")
        sys.stdout.flush()
        sys.stderr.flush()

def request_container_info(socket):

        if sys.version_info < (3, 0):
            socket.send("", zmq.SNDMORE)
        else:
            socket.send_string("", zmq.SNDMORE)
        socket.send(struct.pack("<I", RPC_VERSION))
        socket.send(struct.pack("<I", MESSAGE_TYPE_HEARTBEAT))
        socket.send(struct.pack("<I",HEARTBEAT_TYPE_REQUEST_CONTAINER_METADATA))

        # self.event_history.insert(EVENT_HISTORY_SENT_HEARTBEAT)
        print("Sent container request!")
        sys.stdout.flush()
        sys.stderr.flush()
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://{0}:{1}".format(host_ip,port))

poller = zmq.Poller()
sys.stdout.flush()
sys.stderr.flush()
poller.register(socket, zmq.POLLIN)
connected = False
c = 0
while True:
	receivable_sockets = dict(
                    poller.poll(2000))
	if socket not in receivable_sockets or receivable_sockets[socket] != zmq.POLLIN:
		if connected:
			c += 1
			# time.sleep(2)
			print("Sending heartbeat: {}".format(c))
			sys.stdout.flush()
			sys.stderr.flush()
			request_container_info(socket)
		continue
	if not connected:
		connected = True
	socket.recv()
	msg_type_bytes = socket.recv()
	msg_type = struct.unpack("<I", msg_type_bytes)[0]
	if msg_type == MESSAGE_TYPE_HEARTBEAT:
		print('Recieved the first heartbeat. Now keep the model container connected')
		sys.stdout.flush()
		sys.stderr.flush()
		continue
	if msg_type == MESSAGE_TYPE_NEW_CONTAINER:
		print("Recieved container info")
		sys.stdout.flush()
		sys.stderr.flush()
		info = {}
		model_name = socket.recv_string()
		info['model_name'] = model_name
		model_version = socket.recv_string()

		# model_version = int(model_version)
		info['model_version'] = model_version
		model_input_type = socket.recv_string()
		info['model_input_type'] = model_input_type
		rpc_version_bytes = socket.recv()
		rpc_version = struct.unpack("<I", rpc_version_bytes)[0]
		validate_rpc_version(rpc_version)
		print(info)
		sys.stdout.flush()
		sys.stderr.flush()
		# while True:
			


	# socket = self.context.socket(zmq.DEALER)




