import argparse
import json
import time
import pathlib

from scipy.spatial.distance import cosine
from fastdtw import fastdtw

import cv2
import numpy as np
import torch
from torchvision import transforms

from utils.datasets import letterbox
from utils.torch_utils import select_device
from models.experimental import attempt_load
from utils.general import non_max_suppression_kpt,strip_optimizer
from utils.plots import output_to_keypoint

@torch.no_grad()
def run(poseweights = "yolov7-w6-pose.pt", source = "0", device = 'cpu'):
    
    device = select_device(opt.device) #select device

    model = attempt_load(poseweights, map_location=device)  #Load model
    _ = model.eval()
 
    cap = cv2.VideoCapture(int(source))    #pass video to videocapture object

    if cap.isOpened() == False:   #check if videocapture not opened
        print('Error while trying to read video. Please check path again')
        raise SystemExit()

    else:
        frame_width = int(cap.get(3))  #get video frame width
        frame_height = int(cap.get(4)) #get video frame height

        start = int(time.time())

        while(cap.isOpened): #loop until cap opened or video not complete

            ret, frame = cap.read()  #get frame and success from video capture
            success, realCam = ret, frame

            cv2.imshow("YOLOv7", realCam)

            end = int(time.time())

            if end - start >= 1:
                try:
                    start = int(time.time())

                    orig_image = frame #store frame
                    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB) #convert frame to RGB
                    image = letterbox(image, (frame_width), stride=64, auto=True)[0]
                    image = transforms.ToTensor()(image)
                    image = torch.tensor(np.array([image.numpy()]))

                    image = image.to(device)  #convert image data to device
                    image = image.float() #convert image to float precision (cpu)

                    with torch.no_grad():  #get predictions
                        output_data, _ = model(image)

                    output_data = non_max_suppression_kpt(output_data, 0.25, 0.65, nc = model.yaml['nc'], nkpt = model.yaml['nkpt'], kpt_label = True)

                    output = output_to_keypoint(output_data)

                    output = output[output[:,7].argsort()]

                    left = output[0].reshape(-1, 58).tolist()

                    lmlist_leftuser = []

                    for x in left[0][7:]:
                        lmlist_leftuser.append(int(x))

                    del lmlist_leftuser[2::3]

                    print(lmlist_leftuser)

                except:
                    break

        cap.release()

def parse_opt():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    parser = argparse.ArgumentParser()
    parser.add_argument('--poseweights', nargs='+', type=str, default=path + 'yolov7-w6-pose.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default="0", help='video/0 for webcam') #video source
    parser.add_argument('--device', type=str, default='cpu', help='cpu/0,1,2,3(gpu)')   #device arugments
    opt = parser.parse_args()
    return opt

#main function
def main(opt):
    return run(**vars(opt))

if __name__ == "__main__":
    opt = parse_opt()
    strip_optimizer(opt.device,opt.poseweights)
    main(opt)