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
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]

    # CPU와 GPU 중 어느 하드웨어로 실행 할 지 선택, 기본값 CPU
    device = select_device(opt.device)

    # YOLOv7의 미리 학습된 모델(Weight를 지정, 사람만 감지하는 기본값 파일 yolov7-w6-pose.pt)
    model = attempt_load(poseweights, map_location=device)
    _ = model.eval()
 
    # 캠을 0번째로 지정
    cap = cv2.VideoCapture(int(source))    #pass video to videocapture object

    result = api.gamedata_api(f"/BackgroundData?nickname={nickname}", "GET", None)

    data = json.loads(result)
    coord_name = data["coord_name"]
    
    with open(f"{path}yolov7-pose-estimation/coordinates/{coord_name}.json") as json_file:
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

    # 첫 좌표 값 범위 지정
    a = 0
    b = 34

    # YOLOv7의 17개의 부위, XY 좌표 2개씩 = 34
    # 1초 당 34개의 좌표 불러옴
    while a < b:
        accuracyList.append([json_data[a], json_data[a+1]])
        a += 2

    if cap.isOpened() == False:   #check if videocapture not opened
        print('Error while trying to read video. Please check path again')
        raise SystemExit()

    # 동작 비교 시작
    else:
        frame_width = int(cap.get(3))  #get video frame width

        api.gamedata_api("/ProgramData", "POST", [nickname, 1])

        start = time.time()

        while cap.isOpened: #loop until cap opened or video not complete

            ret, frame = cap.read()  #get frame and success from video capture
            # flipFrame = cv2.flip(frame, 1)
            # ret_val, buffer = cv2.imencode('.jpg', flipFrame)
            # encodedImage = buffer.tobytes()
            # yield (b'--image\r\n'
            #     b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')
            
            end = time.time()

            if end - start >= 1:
                try:
                    # YOLOv7 동작 인식 및 스켈레톤 그리기
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
                        # 대상의 좌표 값 추출
                        output_data = non_max_suppression_kpt(output_data, 0.25, 0.65, nc = model.yaml['nc'], nkpt = model.yaml['nkpt'], kpt_label = True)
                        # 좌표 값 output으로 지정
                        output = output_to_keypoint(output_data)
                        output = output[output[:,7].argsort()]
                        # 왼쪽 사람부터 output의 첫번째 리스트에 저장
                        left = output[0].reshape(-1, 58).tolist()
                        # 왼쪽 사람의 좌표 값 저장 리스트
                        lmlist_leftuser = []
                        # 좌표들을 int 값으로 다시 저장
                        for x in left[0][7:]:
                            lmlist_leftuser.append(int(x))
                        # 사람 인식 테두리 박스 좌표 값 제거
                        del lmlist_leftuser[2::3]
                        # 새로운 변수 리스트에 깔끔한 좌표 값 다시 저장
                        newlmlist_leftuser = []
                        c = 0
                        while c < 34:
                            newlmlist_leftuser.append([lmlist_leftuser[c], lmlist_leftuser[c + 1]])
                            c += 2
                        # 정답 좌표 값과 왼쪽 사람의 좌표 값 비교
                        error_left, _left = fastdtw(newlmlist_leftuser, accuracyList, dist = cosine)

                        if error_left > 1: # Error 1 보다 클 경우 에러 발생 방지
                            error_left = 1
                    
                        if error_left < 0.05: # 95% ~85%
                            perfect_frame_first += 1
                        elif 0.05 <= error_left < 0.15: # 85% ~ 75%
                            awesome_frame_first += 1
                        elif 0.15 <= error_left < 0.25: # 85% ~ 75%
                            good_frame_first += 1
                        elif 0.25 <= error_left < 0.35: # 75% ~ 65%
                            ok_frame_first += 1
                        else:
                            bad_frame_first += 1

                        print("")
                        print("perfect_first", perfect_frame_first)
                        print("awesome_first", awesome_frame_first)
                        print("good_first", good_frame_first)
                        print("ok_first", ok_frame_first)
                        print("bad_first", bad_frame_first)

                        # 여기서부턴 오른쪽 사람 (왼쪽 사람과 같은 알고리즘)
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

                        # 해당 정확도를 리스트 변수에 저장
                        totalAccuracyList.append((capture_time, int((1 - error_left) * 100), int((1 - error_right) * 100)))

                        value = [nickname, totalAccuracyList[-1][0], totalAccuracyList[-1][1], totalAccuracyList[-1][2]]

                        api.gamedata_api("/TwoPlayerData", "POST", value)

                    except:
                        pass

                    # 시간과 관련된 변수 업데이트
                    b += 34
                    accuracyList = []
                    
                    while a < b:
                        accuracyList.append([json_data[a], json_data[a + 1]])
                        a += 2
                    
                    start = time.time()
                    
                except:
                    # 게임이 비정상적으로 종료된 경우
                    # 모든 점수는 0점 처리 후 죄종 정확도 POST
                    if len(totalAccuracyList) != 0:
                        total_left = 0

                        for x in range(0, len(totalAccuracyList)):
                            total_left = total_left + totalAccuracyList[x][1]

                        total_left = int(total_left / len(totalAccuracyList))

                        total_right = 0

                        for x in range(0, len(totalAccuracyList)):
                            total_right = total_right + totalAccuracyList[x][1]

                        total_right = int(total_right / len(totalAccuracyList))

                        value = [nickname, total_left, perfect_frame_first, awesome_frame_first, good_frame_first, ok_frame_first, bad_frame_first, 
                                 total_right, perfect_frame_second, awesome_frame_second, good_frame_second, ok_frame_second, bad_frame_second]

                        api.gamedata_api("/TwoPlayerFinalData", "POST", value)
                    
                    api.gamedata_api("/ProgramData", "POST", [nickname, 0])

                    break

        cap.release()

# YOLOv7 동작 인식 모듈을 실행하기 위한 실행 구문
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