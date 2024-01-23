import argparse
import json
import pathlib
import os

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
    cwd = os.getcwd().replace("\\", "/") + "/"

    onlyfiles = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]

    onlyfiles.remove("yolov7-w6-pose.pt")
    onlyfiles.remove("twoPlayerExtract.py")
    
    device = select_device(opt.device)

    model = attempt_load(poseweights, map_location=device)
    _ = model.eval()

    for y in onlyfiles:
        cap = cv2.VideoCapture(cwd + y)

        fps = round(cap.get(cv2.CAP_PROP_FPS), 0)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]

        frame_width = int(cap.get(3))

        newlmlist_leftuser = []

        while cap.isOpened:
            ret, frame = cap.read()

            if ret:
                timestamps = [int(cap.get(cv2.CAP_PROP_POS_MSEC))]

                if timestamps[-1] % 1000 == 0:
                    try:
                        orig_image = frame
                        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
                        image = letterbox(image, (frame_width), stride=64, auto=True)[0]
                        image = transforms.ToTensor()(image)
                        image = torch.tensor(np.array([image.numpy()]))

                        image = image.to(device)
                        image = image.float()

                        with torch.no_grad():
                            output_data, _ = model(image)

                        print(fps, total_frames, timestamps)

                        output_data = non_max_suppression_kpt(output_data, 0.25, 0.65, nc = model.yaml['nc'], nkpt = model.yaml['nkpt'], kpt_label = True)

                        output = output_to_keypoint(output_data)

                        output = output[output[:,7].argsort()]

                        left = output[0].reshape(-1, 58).tolist()

                        lmlist_leftuser = []

                        for x in left[0][7:]:
                            lmlist_leftuser.append(int(x))

                        del lmlist_leftuser[2::3]

                        newlmlist_leftuser.append(lmlist_leftuser)

                    except:
                        pass

                if timestamps[-1] >= 67000:
                    break

            else:
                cap.release()

        f = open(y + ".json", "x")

        with open(y + ".json", "w") as f:
            json.dump(newlmlist_leftuser, f)

        f.close()

def twoPlayer():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    parser = argparse.ArgumentParser()
    parser.add_argument('--poseweights', nargs='+', type=str, default=path + 'yolov7-w6-pose.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default="0", help='video/0 for webcam')
    parser.add_argument('--device', type=str, default='cpu', help='cpu/0,1,2,3(gpu)')
    global opt
    opt = parser.parse_args()
    strip_optimizer(opt.device,opt.poseweights)
    run(**vars(opt))

twoPlayer()