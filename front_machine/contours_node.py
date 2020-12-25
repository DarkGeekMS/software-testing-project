from config.parser import get_config_from_json
import argparse
import time
import zmq
import cv2
import math

def consumer(addressReceive, addressSend, numTerminate):
    """
    takes  binary image and pushes its contours to the output_node.
    Args:
        addressReceive: string of the ip address followed by the port to make the connection with collector_node.
        addressSend   : string of the ip address followed by the port to make the connection with output_node.
        numTerminate: number of terminates to be sent
    """
    #make the connections
    context = zmq.Context()
    # receive binary image
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect(addressReceive)
    # send its contours to output_node
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect(addressSend)

    TerminationCount = 0

    while True:

        if TerminationCount == numTerminate:
            msg = { 'contours' : [] }
            consumer_sender.send_pyobj(msg)
            break

        #receive the binary frame
        work = consumer_receiver.recv_pyobj()
        data = work['binary']

        if len(data) == 0:
            TerminationCount +=1
            continue

        #get the contours
        contours, _ = cv2.findContours(data, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        result = {'contours' : contours}

        #send the contours
        consumer_sender.send_pyobj(result)

    # wait for the other processes to finish    
    time.sleep(10)    

def main():
    """Main driver of contour consumer node"""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-id', '--node_id', type=int, help='id for the currently running node')

    args = argparser.parse_args()

    config = get_config_from_json("front_machine/config/server.json") # get other nodes addresses from json config

    recv_address = config.remote_sockets[math.floor((args.node_id-1)/2.0)] # get the receive address based on the node id

    consumer(recv_address, config.output_socket, 1) # call the contour consumer process

if __name__=='__main__':
    main()