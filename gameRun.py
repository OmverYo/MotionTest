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

def gameRun():
    try:
        path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

        user_cam = cv2.VideoCapture(0)
        detector = pm.poseDetector()

        totalAccuracyList = []
        capture_time = 0
        perfect_frame = awesome_frame = good_frame = ok_frame = bad_frame = 0

        camDelay = False
        is_vr = False
        result = api.gamedata_api("/BackgroundData", "GET", None)
        data = json.loads(result)

        myVR = data["is_vr"]
        bg_name = data["bg_name"]
        coord_name = data["coord_name"]

        if myVR == 1:
            is_vr = True
        else:
            is_vr = False

        with open(f"{path}coordinates/{coord_name}.json") as json_file:
            json_data = json.load(json_file)

        fbAccuracyList, tbAccuracyList, bbAccuracyList = [], [], []
        a, b, c, d, e, f = 0, 22, 0, 12, 12, 22
        fbAccuracyList, tbAccuracyList, bbAccuracyList = json_data[:b], json_data[:d], json_data[e:f]
        
        start = time.time()
        last_valid_frame = None  # 마지막 유효한 프레임 저장
        
        while True:
            end = time.time()
            if end - start >= 3 and camDelay is False:
                camDelay = True
                api.gamedata_api("/BackgroundData", "DELETE", None)
                api.gamedata_api("/ProgramData", "POST", 1)
            if end - start >= 5:
                break
            
            ret_val, flipFrame = user_cam.read()
            if ret_val:  # 카메라로부터 이미지 데이터가 성공적으로 읽혀진 경우
                flipFrame = cv2.flip(flipFrame, 1)
                try:
                    ret, buffer = cv2.imencode('.jpg', flipFrame)
                    if ret:  # 이미지 인코딩이 성공한 경우
                        flipFrame = buffer.tobytes()
                        last_valid_frame = flipFrame  # 마지막 유효한 프레임 업데이트
                        yield (b'--image\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + flipFrame + b'\r\n')
                except Exception as e:
                    print(f"An error occurred during image encoding: {e}")

        while user_cam.isOpened():
            try:
                ret_val, image_1 = user_cam.read()
                if ret_val:
                    flipFrame = cv2.flip(image_1, 1)
                    flipFrame = detector.findPose(flipFrame)
                    lmList_user = detector.findPosition(flipFrame)
                    handList_user = detector.findHand(flipFrame)
                    topList_user = detector.findTop(flipFrame)
                    bottomList_user = detector.findBottom(flipFrame)

                    value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
                    # api.gamedata_api("/HandData/1", "PUT", value)
                    
                    try:
                        ret, buffer = cv2.imencode('.jpg', flipFrame)
                        if ret:
                            flipFrame = buffer.tobytes()
                            last_valid_frame = flipFrame
                    except Exception as e:
                        print(f"An error occurred during image encoding: {e}")
                    
            except Exception as e:
                print(f"An error occurred during image processing: {e}")
                ret_val = False
            
            # 유효한 프레임이 있는 경우, 혹은 이전에 저장된 유효한 프레임이 있는 경우 전송
            if ret_val or last_valid_frame:
                frame_to_send = flipFrame if ret_val else last_valid_frame
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_to_send + b'\r\n')

            end = time.time()
            if end - start >= 1:
                # 시간과 관련된 변수 업데이트
                capture_time += 1
                b += 22
                d += 10
                f += 12
                fbAccuracyList = json_data[a:b]
                tbAccuracyList = json_data[c:d]
                bbAccuracyList = json_data[e:f]
                a, c, e = b, d, f
            
            ret, buffer = cv2.imencode('.jpg', flipFrame)
            flipFrame = buffer.tobytes()
            yield (b'--image\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + flipFrame + b'\r\n')

        end = time.time()

        if end - start >= 1:
            if lmList_user:
                # 사용자가 카메라 범위 내에 있을 때
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

                totalAccuracyList.append((capture_time, int((1 - errorFull) * 100), int((1 - errorTop) * 100), int((1 - errorBottom) * 100)))
            else:
                # 사용자가 카메라 범위 밖에 있을 때
                print("User is out of camera range")
            
            # 시간과 관련된 변수 업데이트
            capture_time += 1
            b += 22
            d += 10
            f += 12

            value = [capture_time, int((1 - errorFull) * 100) if lmList_user else 0]
            # print(value)
            api.gamedata_api("/AccuracyData", "POST", value)

            print("Ok5")
            totalFull = sum(acc[1] for acc in totalAccuracyList) // capture_time
            totalTop = sum(acc[2] for acc in totalAccuracyList) // capture_time
            totalBottom = sum(acc[3] for acc in totalAccuracyList) // capture_time

            print("Ok6")

            recommend_content = random.randint(25, 152)
            value = [totalFull, totalTop, totalBottom, perfect_frame, awesome_frame, good_frame, ok_frame, bad_frame, recommend_content]
            # print(value)
            api.gamedata_api("/PlayerData", "POST", value)

            print("Ok3")
            fbAccuracyList = json_data[a:b]
            tbAccuracyList = json_data[c:d]
            bbAccuracyList = json_data[e:f]
            a, c, e = b, d, f
            print("Ok4")

            start = time.time()

            if is_vr:
                results = selfie_segmentation.process(flipFrame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.15
                bg_image = cv2.imread(f"{path}static/{bg_name}")
                output_image = np.where(condition, flipFrame, bg_image)
                ret, buffer = cv2.imencode('.jpg', output_image)
                output_image = buffer.tobytes()
                yield (b'--flipFrame\r\n'
                    b'Content-Type: flipFrame/jpeg\r\n\r\n' + output_image + b'\r\n')
            else:
                ret, buffer = cv2.imencode('.jpg', flipFrame)
                flipFrame = buffer.tobytes()
                yield (b'--image\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + flipFrame + b'\r\n')

        user_cam.release()

    except Exception as e:
        print(f"An error occurred: {e}")
        api.gamedata_api("/ProgramData", "DELETE", None)
    finally:
        if user_cam.isOpened():
            print("Ok8")
            user_cam.release()