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

    while user_cam.isOpened():
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        try:
            detectedImage = detector.findPose(image)
            lmList_user = detector.findPosition(detectedImage)
            # handList_user = detector.findHand(detectedImage)
            topList_user = detector.findTop(detectedImage)
            bottomList_user = detector.findBottom(detectedImage)

            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)
                
        except:
            pass

        end = time.time()

        if end - start >= 1:
            try:
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
            
            except:
                errorFull, errorTop, errorBottom = 1, 1, 1
                totalAccuracyList.append((capture_time, int((1 - errorFull) * 100), int((1 - errorTop) * 100), int((1 - errorBottom) * 100)))
            
            # 시간과 관련된 변수 업데이트
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

            start = time.time()

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

    user_cam.release()