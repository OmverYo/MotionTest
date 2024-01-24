import cv2, time, json
import numpy as np
import mediapipe as mp
import poseModule as pm
from scipy.spatial.distance import cosine
from fastdtw import fastdtw
import pathlib
import api
import random

def gameRun():
    # 현재 파일의 위치
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

    # VR 배경 제거를 위한 Mediapipe의 Segmentation 함수
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

    # 유저의 0번째 카메라, Mediapipe의 Pose Detection 함수
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    # 최종 결과 값이 저장될 리스트, 1초 마다 현재 영상의 위치를 기록, 정확도별 프레임 개수를 지정
    totalAccuracyList = []
    capture_time = 0
    perfect_frame = awesome_frame = good_frame = ok_frame = bad_frame = 0

    # 카메라 대기 변수, VR 유무, VR 배경 이름, 좌표 값 이름 
    camDelay = False
    is_vr = False
    result = api.gamedata_api("/BackgroundData", "GET", None)
    data = json.loads(result)

    myVR = data["is_vr"]
    bg_name = data["bg_name"]
    coord_name = data["coord_name"]

    # 불러온 좌표 값 이름이 해당 파일의 이름일 경우 같은 컨텐츠 내에서 추천
    if coord_name.startswith("TK_Poomsae"):
        recommend_content = random.randint(25, 39)

    elif coord_name.startswith("TK_Motion"):
        recommend_content = random.randint(40, 144)

    elif coord_name.startswith("full)") or coord_name.startswith("15_Koyote"):
        recommend_content = random.randint(145, 149)

    elif coord_name.startswith("BX_Motion"):
        recommend_content = random.randint(155, 187)

    # 해당 게임은 VR인지 AR인지 인식
    if myVR == 1:
        is_vr = True
    else:
        is_vr = False

    # 실행되고 비교될 좌표 값 json 파일을 불러옴
    with open(f"{path}coordinates/{coord_name}.json") as json_file:
        json_data = json.load(json_file)

    # 1초 마다 다음으로 넘어갈 현재 좌표 위치 시간대
    fbAccuracyList, tbAccuracyList, bbAccuracyList = [], [], []
    a, b, c, d, e, f = 0, 22, 0, 12, 12, 22
    fbAccuracyList, tbAccuracyList, bbAccuracyList = json_data[:b], json_data[:d], json_data[e:f]
    
    # 1초 마다 현재 시간을 확인
    start = time.time()
    
    # 게임 시작 전 6초간의 대기 시간을 주어 카메라가 실행될 시간을 충분히 제공
    while True:
        end = time.time()
        if end - start >= 3 and camDelay is False:
            camDelay = True
            api.gamedata_api("/BackgroundData", "DELETE", None)
            api.gamedata_api("/ProgramData", "POST", 1)
        if end - start >= 6:
            break
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)

        try:
            if is_vr:
                results = selfie_segmentation.process(flipFrame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.15
                bg_image = cv2.imread(f"{path}{bg_name}")
                output_image = np.where(condition, flipFrame, bg_image)
                ret, buffer = cv2.imencode('.jpg', output_image)
                output_image = buffer.tobytes()
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')
                
            else:
                ret, buffer = cv2.imencode('.jpg', flipFrame)
                frame = buffer.tobytes()
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        except:
            pass

    # 게임 시작 후 카메라 앞 대상을 인식
    while user_cam.isOpened():
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        try:
            detectedImage = detector.findPose(image)
            lmList_user = detector.findPosition(detectedImage)
            topList_user = detector.findTop(detectedImage)
            bottomList_user = detector.findBottom(detectedImage)
            
            # handList_user = detector.findHand(detectedImage)
            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)
                
        except:
            pass

        end = time.time()

        if end - start >= 1:
            try:
                # 대상의 좌표 값과 추출된 좌표 값을 비교, 전신, 상체, 하체
                errorFull, _ = fastdtw(lmList_user, fbAccuracyList, dist=cosine)
                errorTop, _ = fastdtw(topList_user, tbAccuracyList, dist=cosine)
                errorBottom, _ = fastdtw(bottomList_user, bbAccuracyList, dist=cosine)

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

                # 해당 정확도를 리스트 변수에 저장
                totalAccuracyList.append((capture_time, int((1 - errorFull) * 100), int((1 - errorTop) * 100), int((1 - errorBottom) * 100)))
            
            # 카메라에 대상이 없거나 정확도 비교를 실패 할 경우, 최소 오류 없는 정수 1로 지정하여 정확도 0으로 처리
            except:
                errorFull, errorTop, errorBottom = 1, 1, 1
                totalAccuracyList.append((capture_time, int((1 - errorFull) * 100), int((1 - errorTop) * 100), int((1 - errorBottom) * 100)))
            
            # 시간과 관련된 변수 업데이트
            capture_time += 1
            b += 22
            d += 10
            f += 12

            # 1초 마다 업데이트 될 정확도 서버로 전송
            value = [capture_time, int((1 - errorFull) * 100) if lmList_user else 0]
            api.gamedata_api("/AccuracyData", "POST", value)

            # 전신, 상체, 하체의 정확도 개수를 저장
            totalFull = sum(acc[1] for acc in totalAccuracyList) // capture_time
            totalTop = sum(acc[2] for acc in totalAccuracyList) // capture_time
            totalBottom = sum(acc[3] for acc in totalAccuracyList) // capture_time

            value = [totalFull, totalTop, totalBottom, perfect_frame, awesome_frame, good_frame, ok_frame, bad_frame, recommend_content]
            api.gamedata_api("/PlayerData", "POST", value)

            fbAccuracyList = json_data[a:b]
            tbAccuracyList = json_data[c:d]
            bbAccuracyList = json_data[e:f]
            a, c, e = b, d, f

            start = time.time()
        
        # 해당 게임이 AR 중 VR을 선택된 카메라로 HTML로 렌더링
        try:
            if is_vr:
                results = selfie_segmentation.process(flipFrame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.15
                bg_image = cv2.imread(f"{path}{bg_name}")
                output_image = np.where(condition, flipFrame, bg_image)
                ret, buffer = cv2.imencode('.jpg', output_image)
                output_image = buffer.tobytes()
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + output_image + b'\r\n')
                
            else:
                ret, buffer = cv2.imencode('.jpg', flipFrame)
                frame = buffer.tobytes()
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        except:
            pass
    
    # 이 함수의 카메라를 종료
    user_cam.release()