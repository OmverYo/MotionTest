import cv2, time, json
import numpy as np
import mediapipe as mp
import poseModule as pm
from scipy.spatial.distance import cosine
from fastdtw import fastdtw
import pathlib
import api
import random
import logging

# 웸캠에서 프레임을 캡처하는 함수
def capture_frame(user_cam):
    ret_val, frame = user_cam.read()
    if not ret_val:
        return None
    return cv2.flip(frame, 1)

# 캡처된 프레임을 JPEG로 형식으로 인코딩하는 함수
def encode_frame(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes() if ret else None

# 오프라인 모드 함수
def offline_mode():
    user_cam = cv2.VideoCapture(0)
    while True:
        frame = capture_frame(user_cam)
        if frame is None:
            continue
        encoded_frame = encode_frame(frame)
        if encoded_frame:
            yield (b'--image\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n')

# 온라인 모드 함수
def online_mode():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    
    totalAccuracyList = []
    perfect_frame = awesome_frame = good_frame = ok_frame = bad_frame = 0
    camDelay = False
    
    result = api.gamedata_api("/BackgroundData", "GET", None)
    data = json.loads(result)
    coord_name = data["coord_name"]

    # 정답 좌표값 로딩
    with open(f"{path}coordinates/{coord_name}.json") as json_file:
        json_data = json.load(json_file)

    capture_time = 0
    a, b, c, d, e, f = 0, 22, 0, 12, 12, 22
    start = time.time()
    
    fbAccuracyList, tbAccuracyList, bbAccuracyList = [], [], []
    fbAccuracyList, tbAccuracyList, bbAccuracyList = json_data[:b], json_data[:d], json_data[e:f]

    while user_cam.isOpened():
        frame = capture_frame(user_cam)
        if frame is None:
            continue

        processed_frame = detector.findPose(frame)
        lmList_user = detector.findPosition(processed_frame)
        encoded_frame = encode_frame(processed_frame)

        # 사용자 좌표값 처리 및 데이터 송수신
        if lmList_user:
            # 좌표값 비교 로직
            errorFull, _ = fastdtw(lmList_user, json_data[a:b], dist=cosine)
            errorTop, _ = fastdtw(lmList_user, json_data[c:d], dist=cosine)
            errorBottom, _ = fastdtw(lmList_user, json_data[e:f], dist=cosine)

            
            errorFull, errorTop, errorBottom = min(errorFull, 1), min(errorTop, 1), min(errorBottom, 1)
            
            if errorFull < 0.05: # 95 % 
                perfect_frame += 1
            elif 0.05 <= errorFull < 0.15: # 95% ~85%
                awesome_frame += 1
            elif 0.15 <= errorFull < 0.25: # 85% ~ 75%
                good_frame += 1
            elif 0.25 <= errorFull < 0.35: # 75% ~ 65%
                ok_frame += 1
            else:
                bad_frame += 1

            totalAccuracyList.append((capture_time, int((1 - errorFull) * 100), int((1 - errorTop) * 100), int((1 - errorBottom) * 100)))
            
            # DB 송수신 로직
        else:
            # 사용자가 카메라 범위 밖에 있을 때
            print("User is out of camera range")
            
        # 시간 업데이트
        end = time.time()
        if end - start >= 1:
            capture_time += 1
            b += 22
            d += 10
            f += 12
            
            value = [capture_time, int((1 - errorFull) * 100) if lmList_user else 0]
            api.gamedata_api("/AccuracyData", "POST", value)
            
            totalFull = sum(acc[1] for acc in totalAccuracyList) // capture_time
            totalTop = sum(acc[2] for acc in totalAccuracyList) // capture_time
            totalBottom = sum(acc[3] for acc in totalAccuracyList) // capture_time
            
            recommend_content = random.randint(25, 152)
            value = [totalFull, totalTop, totalBottom, perfect_frame, awesome_frame, good_frame, ok_frame, bad_frame, recommend_content]
            api.gamedata_api("/PlayerData", "POST", value)
            
            fbAccuracyList = json_data[a:b]
            tbAccuracyList = json_data[c:d]
            bbAccuracyList = json_data[e:f]
            a, c, e = b, d, f
            
            start = end
        
        user_cam.release()

        if encoded_frame:
            yield (b'--image\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n')

# 네트워크 상태에 따라 적절한 모드 선택 및 실행
# 예시: if is_online(): online_mode() else: offline_mode()
