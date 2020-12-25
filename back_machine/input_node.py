from config.parser import get_config_from_json
import argparse
import time
import zmq
import cv2

def producer(address, videoPath, numTerminate):
    """
    takes video and pushes its frame.
    Args:
        address     : string of the ip address followed by the port to make the connection with ostu_node.
        videoPath   : string path to any video.
        numTerminate: number of terminates to be sent
    """
    #make the connections
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind(address)

    #open the video
    cap = cv2.VideoCapture(videoPath)

    #if video not exists exit with error message
    if (cap.isOpened()== False):
        print("Error opening video file")
        exit()

    # Read until video is completed
    while(cap.isOpened()):
        # get frame by frame from the video
        ret, frame = cap.read()
        if ret == True:
            #convert the frame to gray scaled one
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # keep the frame in dictionary to send it as json object
            work_message = { 'frame' : gray }

            #send the frame
            zmq_socket.send_pyobj(work_message)
        # if error occurs break the loop
        else:
            break

    for i in range (numTerminate):
        work_message = { 'frame': [] }
        zmq_socket.send_pyobj(work_message)
    # When everything done, release the video capture object
    cap.release()

    # wait for the other processes to finish
    time.sleep(10)

def main():
    """Main driver of input node"""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-v', '--video_path', type=str, help='path to the input video')
    argparser.add_argument('-n', '--total_num', type=int, help='total number of consumer nodes')
    
    args = argparser.parse_args()

    config = get_config_from_json("back_machine/config/server.json") # get other nodes addresses from json config

    producer(config.input_socket, args.video_path, args.total_num) # call the producer process

if __name__=='__main__':
    main()