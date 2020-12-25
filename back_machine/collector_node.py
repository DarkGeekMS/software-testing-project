from config.parser import get_config_from_json
import argparse
import time
from math import ceil
import zmq

def collector(addressReceive, addressSend, numTerminate):
    """
    takes  binary image and pushes it to the contours_node.
    Args:
        addressReceive: string of the ip address followed by the port to make the connection with ostu_node.
        addressSend   : string of the ip address followed by the port to make the connection with contours_node.
        numTerminate: number of terminates to be sent
    """
    #make the connections
    context = zmq.Context()
    # receive binary image
    collector_receiver = context.socket(zmq.PULL)
    collector_receiver.bind(addressReceive)
    # send the binary image to contours_node
    collector_sender = context.socket(zmq.PUSH)
    collector_sender.bind(addressSend)
    TerminationCount = 0

    while True:

        if TerminationCount == numTerminate:
            for i in range(numTerminate):
                msg = { 'binary' : [] }
                collector_sender.send_pyobj(msg)  
            break

        #get the frames from ostu node and send them to contours node
        work = collector_receiver.recv_pyobj()
        if len(work['binary']) == 0:
            TerminationCount +=1
            continue
        collector_sender.send_pyobj(work)

    # wait for the other processes to finish    
    time.sleep(10)    

def main():
    """Main driver of collector node"""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-id', '--node_id', type=int, help='id for the currently running node')
    argparser.add_argument('-n', '--total_num', type=int, help='total number of consumer nodes')

    args = argparser.parse_args()

    num_terminate = 0
    if (args.total_num % 2 == 0):
        num_terminate = 2
    else:
        if (args.node_id == ceil(args.total_num/2.0)):
            num_terminate = 1
        else:
            num_terminate = 2
            
    config = get_config_from_json("back_machine/config/server.json") # get other nodes addresses from json config

    recv_address = config.collector_sockets[args.node_id-1] # get the receive address based on the node id
    send_address = config.remote_sockets[args.node_id-1] # get the send address based on the node id

    collector(recv_address, send_address, num_terminate) # call the OTSU collector process

if __name__=='__main__':
    main()