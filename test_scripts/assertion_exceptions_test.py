"""
This script is used to test the skip marker feature on OTSU node module
"""
import pytest
import sys
import time
import numpy as np
from threading import Thread
from front_machine.contours_node import consumer
import time

# check missing import dependency for opencv and pyzmq
cv2 = pytest.importorskip("cv2")
zmq = pytest.importorskip("zmq")

# define in and out ports
port_counter = 0

in_ports = ["tcp://127.0.0.1:5999", 
            "tcp://127.0.0.1:6000"]
out_ports = ["tcp://127.0.0.1:6666",
            "tcp://127.0.0.1:6667"]

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

class TestContours:
    @pytest.fixture(autouse=True)
    def _init_test_sockets(self, init_in_socket, init_out_socket):
        # pytest fixture to set in and out sockets
        self.in_socket = init_in_socket
        self.out_socket = init_out_socket


    def test_contours_output(self):

        global port_counter
        thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
        thread.start()

        port_counter += 1

        im = cv2.imread("back_machine/inputs/test_image.png")
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        threshold, binary = cv2.threshold(imgray , 0 , 255 , cv2.THRESH_OTSU)
        
        in_message = { 'binary' : binary}

        self.in_socket.send_pyobj(in_message)

        assert thread.is_alive(), "Contours thread is dead"

        thread.join()
        # read return message from output socket
        ret_message = self.out_socket.recv_pyobj()

        contours = ret_message['contours']

        assert len(contours) > 0, "Contours list are empty"
        

        # assert type of message

    def test_type_error(self):

        global port_counter

        with pytest.raises(zmq.ZMQError):

            thread = Thread(target = consumer, args = (in_ports[port_counter], out_ports[port_counter], 1, True))
            thread.start()

            in_message = { 'binary' : 0.5}

            self.in_socket.send_pyobj(in_message)

            time.sleep(1)

            thread.join()

            ret_message = self.out_socket.recv_pyobj(flags = zmq.NOBLOCK)


