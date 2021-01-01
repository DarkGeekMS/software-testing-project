import pytest
import time
import zmq
import cv2
import random

from threading import Thread
from back_machine.collector_node import collector
from back_machine.input_node import producer
from back_machine.ostu_node import consumer as otsu_consumer
from front_machine.contours_node import consumer as contours_consumer
from front_machine.output_node import result_collector


# fixtures with module scope to handle global variables and destroyed with the last test in the module
@pytest.fixture(scope = 'module')
def context():
    context = zmq.Context()
    return context

@pytest.fixture(scope = 'module')
def in_port():
    return "tcp://127.0.0.1:5500"

@pytest.fixture(scope = 'module')
def out_port():
    return "tcp://127.0.0.1:5501"

@pytest.fixture(scope = 'module')
def num_nodes():
    return random.randint(2, 20) 

# fixtures with function scope that get destroyed with the teardown of the function
# fixtures that request multi-fixtures
# Modularity: using fixtures from a fixture function

class BindSockets:
    def __init__(self, context, in_port, out_port):
        self.context = context
        self.in_port = in_port
        self.out_port = out_port
        
        self.init_in_socket = self.init_in_socket_bind()
        self.init_out_socket = self.init_out_socket_bind()
    
    def init_in_socket_bind(self):
        zmq_socket = self.context.socket(zmq.PUSH)
        zmq_socket.bind(self.in_port)
        return zmq_socket

    def init_out_socket_bind(self):
        zmq_socket = self.context.socket(zmq.PULL)
        zmq_socket.bind(self.out_port)
        return zmq_socket

class ConnectSockets:
    def __init__(self, context, in_port, out_port):
        self.context = context
        self.in_port = in_port
        self.out_port = out_port
        
        self.init_in_socket = self.init_in_socket_connect()
        self.init_out_socket = self.init_out_socket_connect()
    
    def init_in_socket_connect(self):
        zmq_socket = self.context.socket(zmq.PUSH)
        zmq_socket.connect(self.in_port)
        return zmq_socket

    def init_out_socket_connect(self):
        zmq_socket = self.context.socket(zmq.PULL)
        zmq_socket.connect(self.out_port)
        return zmq_socket


@pytest.fixture(scope = 'function')
def init_sockets(request, context, in_port, out_port):
    socket_type = request.node.get_closest_marker("type").args[0]
    if socket_type == 'connect':
        sockets = ConnectSockets(context, in_port, out_port)
    elif socket_type == 'bind':
        sockets = BindSockets(context, in_port, out_port)
    
    yield sockets

    # release the sockets before running other tests
    sockets.init_in_socket.close()
    sockets.init_out_socket.close()
    

class TestReqMultiFixtures:

    # autouse fixture to be called with each test
    @pytest.fixture(autouse=True)
    def _init_sockets(self, init_sockets):
        self.in_socket = init_sockets.init_in_socket
        self.out_socket = init_sockets.init_out_socket



    @pytest.mark.type('connect')
    # test that requests multi-fixtures
    def test_input_terminate(self, out_port, num_nodes):
        """
        Test the termination of input node
        TEST TYPE : connect
        """
        # input node that should send termination after finishing sending the video frames to otsu nodes
        input_thread = Thread(target = producer, args = (out_port, './back_machine/inputs/1.mp4', num_nodes))
        input_thread.start()

        # count number of frames in the video
        cap = cv2.VideoCapture('./back_machine/inputs/1.mp4')
        frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # receiving frames from input node
        for i in range(frames_count):
            # make sure that input node is alive
            assert input_thread.is_alive(), "input node thread died before sending all frames, test failed!"
            frame_msg = self.out_socket.recv_pyobj()

        # receiving num_nodes empty termination msgs from input node
        for i in range(num_nodes):
            termination_msg = self.out_socket.recv_pyobj()
            # make sure that termination msgs are all empty
            assert len(termination_msg['frame']) == 0, "termination msg is not empty!"

        # wait till the input node dies
        time.sleep(0.01)
        # make sure that input node dies after sending termination msgs
        assert not input_thread.is_alive(), "input node thread is still alive after s terminations, test failed!"
        input_thread.join()





    @pytest.mark.type('connect')
    # test that requests multi-fixtures
    def test_collector_terminate(self, in_port, out_port, num_nodes):
        """
        Test the termination of collector node
        TEST TYPE : connect
        """
        # collector that needs num_nodes empty received msgs to terminate
        collector_thread = Thread(target = collector, args = (in_port, out_port, num_nodes))
        collector_thread.start()
        empty_message = { 'binary' : [] }

        # sending num_nodes empty msgs to collector
        for i in range(num_nodes):
            # make sure that collector is alive
            assert collector_thread.is_alive(), "collector node thread died before num_nodes receives, test failed!"
            self.in_socket.send_pyobj(empty_message)

        # receiving num_nodes empty termination msgs from the collector
        for i in range(num_nodes):
            termination_msg = self.out_socket.recv_pyobj()
            # make sure that termination msgs are all empty
            assert len(termination_msg['binary']) == 0, "termination msg is not empty!"

        # wait till the collector dies
        time.sleep(0.01)
        # make sure that collector dies after sending termination msgs
        assert not collector_thread.is_alive(), "collector node thread is still alive after num_nodes terminations, test failed!"
        collector_thread.join()




    @pytest.mark.type('bind')
    # test that requests multi-fixtures
    def test_otsu_terminate(self, in_port, out_port, num_nodes):
        """
        Test the termination of otsu node
        TEST TYPE : bind
        """
        # otsu_consumer that needs num_nodes empty received msgs to terminate
        consumer_thread = Thread(target = otsu_consumer, args = (in_port, out_port, num_nodes))
        consumer_thread.start()
        empty_message = { 'frame' : [] }

        # sending num_nodes empty msgs to otsu_consumer
        for i in range(num_nodes):
            # make sure that otsu_consumer is alive
            assert consumer_thread.is_alive(), "otsu_consumer node thread died before num_nodes receives, test failed!"
            self.in_socket.send_pyobj(empty_message)
        

        # receiving 1 empty termination msg from the otsu_consumer
        termination_msg = self.out_socket.recv_pyobj()
        # make sure that termination msg is empty
        assert len(termination_msg['binary']) == 0, "termination msg is not empty!"
            
        # wait till the otsu_consumer dies
        time.sleep(0.01)
        # make sure that otsu_consumer dies after sending termination msg
        assert not consumer_thread.is_alive(), "otsu_consumer node thread is still alive after the termination msg, test failed!"
        consumer_thread.join()

        



    @pytest.mark.type('bind')
    # test that requests multi-fixtures
    def test_contours_terminate(self, in_port, out_port, num_nodes):
        """
        Test the termination of contours node
        TEST TYPE : bind
        """
        # contours_consumer that needs num_nodes empty received msgs to terminate
        consumer_thread = Thread(target = contours_consumer, args = (in_port, out_port, num_nodes))
        consumer_thread.start()
        empty_message = { 'binary' : [] }

        # sending num_nodes empty msgs to contours_consumer
        for i in range(num_nodes):
            # make sure that contours_consumer is alive
            assert consumer_thread.is_alive(), "contours_consumer node thread died before num_nodes receives, test failed!"
            self.in_socket.send_pyobj(empty_message)
        

        # receiving 1 empty termination msg from the contours_consumer
        termination_msg = self.out_socket.recv_pyobj()
        # make sure that termination msg is empty
        assert len(termination_msg['contours']) == 0, "termination msg is not empty!"
            
        # wait till the contours_consumer dies
        time.sleep(0.01)
        # make sure that contours_consumer dies after sending termination msg
        assert not consumer_thread.is_alive(), "contours_consumer node thread is still alive after the termination msg, test failed!"
        consumer_thread.join()

        

    @pytest.mark.type('connect')
    # test that requests multi-fixtures
    def test_output_terminate(self, in_port, num_nodes):
        """
        Test the termination of output node
        TEST TYPE : connect
        """
        # output node that should send termination after finishing sending the video frames to otsu nodes
        output_thread = Thread(target = result_collector, args = (in_port, './', num_nodes))
        output_thread.start()
        empty_message = { 'contours' : [] }

        # sending num_nodes empty termination msgs to output node
        for i in range(num_nodes):
            # make sure that output node is alive
            assert output_thread.is_alive(), "output node thread died before receiving all terminations, test failed!"
            self.in_socket.send_pyobj(empty_message)
        
        # wait till the output node dies
        time.sleep(1)
        # make sure that output node dies after receiving termination msgs
        assert not output_thread.is_alive(), "output node thread is still alive after receiving all terminations, test failed!"
        output_thread.join()

        
