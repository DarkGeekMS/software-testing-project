import pytest
import sys
import time
import zmq
import cv2
import numpy as np
from unittest import mock
from threading import Thread
from back_machine.ostu_node import get_binary
from back_machine.ostu_node import random_sum

# class to test the mock on ostu node
class TestMockOSTU:
    @pytest.fixture(autouse=True)
    def _init_test_sockets(self):
        #read the image and convet it to binary 
        self.img = cv2.imread('back_machine/inputs/test_image.png', cv2.IMREAD_GRAYSCALE)
        binary = np.zeros_like(self.img)
        self.binary2 = np.zeros_like(self.img)
        r,c = np.shape(self.img)
        #get the right binary image
        for i in range(r):
            for j in range(c):
                if self.img[i][j] > 150:
                    binary[i][j] = 1
        # the binary images
        self.binary1 = binary
    #definedparameters to make connections
    #define mock connection to ostu node
    @mock.patch("back_machine.ostu_node.cv2.threshold" ,autospec = True)
    def test_otsu_threshold_pass(self ,mock_threshold):
        #set the mock side effects
        mock_threshold.side_effect = [[150,self.binary1], [255, self.binary2]]
        # create a thread for OTSU node

        # assert value of message
        assert ((get_binary(self.img) == self.binary1).all()), "The binary image is incorrect!"
        
    #define mock connection to ostu node
    @mock.patch("back_machine.ostu_node.cv2.threshold" ,autospec = True)
    def test_otsu_threshold_fail(self ,mock_threshold):
        #set the mock side effects
        mock_threshold.side_effect = [[150,self.binary1], [255, self.binary2]]
        # create a thread for OTSU node

        # assert value of message
        assert ((get_binary(self.img) == self.binary2).all()), "The binary image is incorrect!"
        
    #definedparameters to make connections
    @pytest.mark.parametrize("value,expected", [(1, 5 ), (2, 5 )], ids=["t3", "t4"])
    #define mock connection to ostu node
    @mock.patch("back_machine.ostu_node.random.randint")
    def test_otsu_random(self, mock_randint, value, expected):

        mock_randint.side_effect = [4 , 5]
        assert random_sum(value) == expected, "summation is wrong"
        


