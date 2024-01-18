import argparse
import json
import time
import pathlib
import api

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
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    
    device = select_device(opt.device) #select device

    model = attempt_load(poseweights, map_location=device)  #Load model
    _ = model.eval()
 
    cap = cv2.VideoCapture(int(source))    #pass video to videocapture object

    result = api.gamedata_api("/BackgroundData", "GET", None)

    data = json.loads(result)
    coord_name = data["coord_name"]
    
    with open(f"{path}/yolov7-pose-estimation/coordinates/{coord_name}.json") as json_file:
        json_data = json.load(json_file)

    accuracyList = []

    totalAccuracyList = []

    capture_time = 0

    perfect_frame_first = 0
    awesome_frame_first = 0
    good_frame_first = 0
    ok_frame_first = 0
    bad_frame_first = 0
    perfect_frame_second = 0
    awesome_frame_second = 0
    good_frame_second = 0
    ok_frame_second = 0
    bad_frame_second = 0

    a = 0
    b = 34

    while a < b:
        accuracyList.append([json_data[a], json_data[a+1]])
        a += 2

    if cap.isOpened() == False:   #check if videocapture not opened
        print('Error while trying to read video. Please check path again')
        raise SystemExit()

    else:
        frame_width = int(cap.get(3))  #get video frame width

        api.gamedata_api("/BackgroundData", "DELETE", None)

        api.gamedata_api("/ProgramData", "POST", True)

        start = time.time()

        while cap.isOpened: #loop until cap opened or video not complete

            ret, frame = cap.read()  #get frame and success from video capture
            
            end = time.time()

            if end - start >= 1:
                try:
                    orig_image = frame #store frame
                    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB) #convert frame to RGB
                    image = letterbox(image, (frame_width), stride=64, auto=True)[0]
                    image = transforms.ToTensor()(image)
                    image = torch.tensor(np.array([image.numpy()]))

                    image = image.to(device)  #convert image data to device
                    image = image.float() #convert image to float precision (cpu)

                    with torch.no_grad():  #get predictions
                        output_data, _ = model(image)

                    try:
                        capture_time += 1

                        output_data = non_max_suppression_kpt(output_data, 0.25, 0.65, nc = model.yaml['nc'], nkpt = model.yaml['nkpt'], kpt_label = True)

                        output = output_to_keypoint(output_data)

                        output = output[output[:,7].argsort()]

                        left = output[0].reshape(-1, 58).tolist()

                        lmlist_leftuser = []

                        for x in left[0][7:]:
                            lmlist_leftuser.append(int(x))

                        del lmlist_leftuser[2::3]

                        newlmlist_leftuser = []
                        c = 0

                        while c < 34:
                            newlmlist_leftuser.append([lmlist_leftuser[c], lmlist_leftuser[c + 1]])
                            c += 2
                        
                        error_left, _left = fastdtw(newlmlist_leftuser, accuracyList, dist = cosine)

                        if error_left > 1:
                            error_left = 1
                        
                        if error_left < 0.05:
                            perfect_frame_first += 1

                        elif error_left < 0.15 and error_left > 0.05:
                            awesome_frame_first += 1

                        elif error_left < 0.3 and error_left > 0.16:
                            good_frame_first += 1

                        elif error_left < 0.5 and error_left > 0.31:
                            ok_frame_first += 1

                        elif error_left > 0.5:
                            bad_frame_first += 1

                        print("")
                        print("perfect_first", perfect_frame_first)
                        print("awesome_first", awesome_frame_first)
                        print("good_first", good_frame_first)
                        print("ok_first", ok_frame_first)
                        print("bad_first", bad_frame_first)

                        right = output[1].reshape(-1, 58).tolist()

                        lmlist_rightuser = []

                        for y in right[0][7:]:
                            lmlist_rightuser.append(int(y))

                        del lmlist_rightuser[2::3]

                        newlmlist_rightuser = []
                        c = 0

                        while c < 34:
                            newlmlist_rightuser.append([lmlist_rightuser[c], lmlist_rightuser[c + 1]])
                            c += 2

                        error_right, _right = fastdtw(newlmlist_rightuser, accuracyList, dist = cosine)
                        
                        if error_right > 1:
                            error_right = 1
                        
                        if error_right < 0.05:
                            perfect_frame_second += 1

                        elif error_right < 0.15 and error_right > 0.05:
                            awesome_frame_second += 1

                        elif error_right < 0.3 and error_right > 0.16:
                            good_frame_second += 1

                        elif error_right < 0.5 and error_right > 0.31:
                            ok_frame_second += 1

                        elif error_right > 0.5:
                            bad_frame_second += 1

                        print("")
                        print("perfect_second", perfect_frame_second)
                        print("awesome_second", awesome_frame_second)
                        print("good_second", good_frame_second)
                        print("ok_second", ok_frame_second)
                        print("bad_second", bad_frame_second)

                        totalAccuracyList.append((capture_time, int((1 - error_left) * 100), int((1 - error_right) * 100)))

                        value = [totalAccuracyList[-1][0], totalAccuracyList[-1][1], totalAccuracyList[-1][2]]

                        api.gamedata_api("/TwoPlayerData", "POST", value)

                    except:
                        pass

                    b += 34
                    accuracyList = []
                    
                    while a < b:
                        accuracyList.append([json_data[a], json_data[a + 1]])
                        a += 2
                    
                    start = time.time()
                    
                except:
                    api.gamedata_api("/ProgramData", "DELETE", None)

                    if len(totalAccuracyList) != 0:
                        total_left = 0

                        for x in range(0, len(totalAccuracyList)):
                            total_left = total_left + totalAccuracyList[x][1]

                        total_left = int(total_left / len(totalAccuracyList))

                        total_right = 0

                        for x in range(0, len(totalAccuracyList)):
                            total_right = total_right + totalAccuracyList[x][1]

                        total_right = int(total_right / len(totalAccuracyList))

                        value = [total_left, perfect_frame_first, awesome_frame_first, good_frame_first, ok_frame_first, bad_frame_first, 
                                 total_right, perfect_frame_second, awesome_frame_second, good_frame_second, ok_frame_second, bad_frame_second]

                        api.gamedata_api("/TwoPlayerFinalData", "POST", value)
                    
                    break

        cap.release()

def twoPlayer():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    parser = argparse.ArgumentParser()
    parser.add_argument('--poseweights', nargs='+', type=str, default=path + 'yolov7-w6-pose.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default="0", help='video/0 for webcam') #video source
    parser.add_argument('--device', type=str, default='cpu', help='cpu/0,1,2,3(gpu)')   #device arugments
    global opt
    opt = parser.parse_args()
    strip_optimizer(opt.device,opt.poseweights)
    run(**vars(opt))