"""
This script is used to test the skip marker feature on OTSU node module
"""
import pytest
import cv2
import zmq
import numpy as np
from threading import Thread
from back_machine.ostu_node import consumer

# define in and out ports
port_counter = 0
in_ports = ["tcp://127.0.0.1:5560", 
            "tcp://127.0.0.1:5561", 
            "tcp://127.0.0.1:5562", 
            "tcp://127.0.0.1:5563", 
            "tcp://127.0.0.1:5564", 
            "tcp://127.0.0.1:5565"]
out_ports = ["tcp://127.0.0.1:5570",
            "tcp://127.0.0.1:5571",
            "tcp://127.0.0.1:5572",
            "tcp://127.0.0.1:5573",
            "tcp://127.0.0.1:5574",
            "tcp://127.0.0.1:5575"]

@pytest.fixture()
def init_in_socket():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind(in_ports[port_counter])
    return zmq_socket

@pytest.fixture()
def init_out_socket():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PULL)
    zmq_socket.bind(out_ports[port_counter])
    return zmq_socket

class TestSkipOTSU:

    @pytest.fixture(autouse=True)
    def _init_test_sockets(self, init_in_socket, init_out_socket):
        self.in_socket = init_in_socket
        self.out_socket = init_out_socket

    def test_connection(self):
        global port_counter
        img = cv2.imread('back_machine/inputs/test_image.png', cv2.IMREAD_GRAYSCALE)
        thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
        thread.start()
        in_message = { 'frame' : img }
        self.in_socket.send_pyobj(in_message)
        thread.join()
        port_counter += 1
        ret_message = self.out_socket.recv_pyobj()
        frame = ret_message['binary']
        assert type(frame).__module__ == np.__name__, "OTSU node return is invalid!"

    def test_output(self):
        global port_counter
        port_counter += 1

    def test_terminate(self):
        global port_counter
        port_counter += 1
    
    def test_wrong_input(self):
        global port_counter
        port_counter += 1

    def test_wrong_port(self):
        global port_counter
        port_counter += 1

    def test_occupied_port(self):
        global port_counter
        port_counter += 1
