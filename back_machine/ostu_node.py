from config.parser import get_config_from_json
import argparse
import time
import zmq
import cv2
import math

def consumer(addressReceive, addressSend, numTerminate):
    """
    takes video frame and pushes its binary image.
    Args:
        addressReceive: string of the ip address followed by the port to make the connection with input_node.
        addressSend   : string of the ip address followed by the port to make the connection with collector_node.
        numTerminate: number of terminates to be sent
    """
    #make the connections
    context = zmq.Context()
    # receive video frames
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect(addressReceive)
    # send binary result
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect(addressSend)
    TerminationCount = 0

    while True:

        if TerminationCount == numTerminate:
            msg = { 'binary' : [] }
            consumer_sender.send_pyobj(msg)
            break
        #receive the frame (grayScaled)
        work = consumer_receiver.recv_pyobj()
        frame = work['frame']

        if len(frame) == 0:
            TerminationCount +=1
            continue

        #apply ostu thresholding technique on it
        threshold, binary = cv2.threshold(frame , 0 , 255 , cv2.THRESH_OTSU)
        msg = {'binary' : binary}
        #push the binary result to the collector
        consumer_sender.send_pyobj(msg)

    # wait for the other processes to finish    
    time.sleep(10)    

def main():
    """Main driver of ostu consumer node"""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-id', '--node_id', type=int, help='id for the currently running node')

    args = argparser.parse_args()

    config = get_config_from_json("back_machine/config/server.json") # get other nodes addresses from json config

    send_address = config.collector_sockets[math.floor((args.node_id-1)/2.0)] # get the send address based on the node id

    consumer(config.input_socket, send_address, 1) # call the OTSU consumer process

if __name__=='__main__':
    main()            