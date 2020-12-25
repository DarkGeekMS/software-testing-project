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

# define pytest fixture to allocate in ports
@pytest.fixture()
def init_in_socket():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind(in_ports[port_counter])
    return zmq_socket

# define pytest fixture to allocate out ports
@pytest.fixture()
def init_out_socket():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PULL)
    zmq_socket.bind(out_ports[port_counter])
    return zmq_socket

# OTSU node skip test class
class TestSkipOTSU:

    @pytest.fixture(autouse=True)
    def _init_test_sockets(self, init_in_socket, init_out_socket):
        # pytest fixture to set in and out sockets
        self.in_socket = init_in_socket
        self.out_socket = init_out_socket

    def test_connection(self):
        # test OSTU node connection
        global port_counter
        # read RGB image as greyscale
        img = cv2.imread('back_machine/inputs/test_image.png', cv2.IMREAD_GRAYSCALE)
        # create a thread for OTSU node
        thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
        # start OTSU node thread
        thread.start()
        # send greyscale image through input socket
        in_message = { 'frame' : img }
        self.in_socket.send_pyobj(in_message)
        # join OTSU node thread
        thread.join()
        port_counter += 1
        # read return message from output socket
        ret_message = self.out_socket.recv_pyobj()
        frame = ret_message['binary']
        # assert type of message
        assert type(frame).__module__ == np.__name__, "OTSU node return is invalid!"

    def test_output(self):
        # test OSTU node output validity
        global port_counter
        # read RGB image as greyscale
        img = cv2.imread('back_machine/inputs/test_image.png', cv2.IMREAD_GRAYSCALE)
        # threshold greyscale image
        threshold, binary = cv2.threshold(img , 0 , 255 , cv2.THRESH_OTSU)
        # create a thread for OTSU node
        thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
        # start OTSU node thread
        thread.start()
        # send greyscale image through input socket
        in_message = { 'frame' : img }
        self.in_socket.send_pyobj(in_message)
        # join OTSU node thread
        thread.join()
        port_counter += 1
        # read return message from output socket
        ret_message = self.out_socket.recv_pyobj()
        frame = ret_message['binary']
        # assert value of message
        assert (binary == frame).all(), "The output image of OTSU node is incorrect!"

    def test_terminate(self):
        # test OSTU node output validity
        global port_counter
        # create a thread for OTSU node
        thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
        # start OTSU node thread
        thread.start()
        # send an empty list through input socket
        in_message = { 'frame' : list() }
        self.in_socket.send_pyobj(in_message)
        # join OTSU node thread
        thread.join()
        port_counter += 1
        # read return message from output socket
        ret_message = self.out_socket.recv_pyobj()
        frame = ret_message['binary']
        # assert value of message
        assert len(frame) == 0, "The output is not empty upon termination!"
    
    def test_wrong_input(self):
        global port_counter
        port_counter += 1

    def test_wrong_port(self):
        global port_counter
        port_counter += 1

    def test_occupied_port(self):
        global port_counter
        port_counter += 1
