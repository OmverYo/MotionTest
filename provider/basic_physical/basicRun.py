import cv2, time
from provider import poseModule as pm
import random
from provider import api
import playsound as ps
import pathlib
import json

# 두 발목의 거리 차이를 계산
def distanceCalculate(p1, p2):
    """p1 and p2 in format (x1, y1) and (x2, y2) tuples"""
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    
    return dis

def basicRun():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]

    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    randomCounter = random.randint(2, 5)

    counterResult = []

    camDelay = False
    Start = 0
    Count = 0

    startTimer = time.time()
    endTimer = time.time()

    while True:
        endTimer = time.time()
        if endTimer - startTimer >= 3 and camDelay is False:
            camDelay = True
            api.gamedata_api("/BackgroundData", "DELETE", None)
            api.gamedata_api("/ProgramData", "POST", [nickname, 1])
        if endTimer - startTimer >= 6:
            startTimer = time.time()
            break
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        ret, buffer = cv2.imencode('.jpg', flipFrame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
    while user_cam.isOpened():
        success, image = user_cam.read()
        
        try:
            image = detector.findPose(image)
            results = detector.findAnkle(image)
            # handList_user = detector.findHand(image)

            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 2:
                leftAnkle = [results[0][1], results[0][2]]
                rightAnkle = [results[1][1], results[1][2]]

                # 총 3번 완료시 종료
                if Count >= 3:
                    y = 0

                    for x in counterResult:
                        y += x

                    y = round(y / 3, 3)

                    # rating = 0

                    # if y >= 0.500:
                    #     rating = 0

                    # else:
                    #     rating = 1

                    value = [nickname, y, 0, 0, 0, 0, 0]

                    api.gamedata_api("/BasicData", "POST", value)
                    api.gamedata_api(f"/BasicData/{nickname}/update_rating", "PUT", value)

                    break

                if Start and endTimer - startTimer >= randomCounter:
                    ps.playsound(path + "static/start.mp3")

                    startTimer = time.time()

                # 발목이 다시 좁아지면 시작
                if distanceCalculate(leftAnkle, rightAnkle) < 50:
                    Start = 1
                    endTimer = time.time()

                # 발목 사이 길이가 넓어지면 카운트 1
                elif Start and distanceCalculate(leftAnkle, rightAnkle) > 60:
                    endTimer = time.time()
                    
                    Count = Count + 1
                    Start = 0

                    counterResult.append(round((endTimer - startTimer), 3))
                    print("Time Taken:", round((endTimer - startTimer), 3))

                    randomCounter = random.randint(2, 5)

                    print("Random:", randomCounter)
                    print("Count:", Count)

                    startTimer = time.time()

                else:
                    pass

        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')
    
    startTimer = time.time()

    while True:
        endTimer = time.time()

        if endTimer - startTimer >= 3:
            user_cam.release()
            
            api.gamedata_api("/ProgramData", "POST", [nickname, 0])
            
            break
        
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        ret, buffer = cv2.imencode('.jpg', flipFrame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')