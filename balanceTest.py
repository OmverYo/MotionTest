import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib
import json

def differenceCalculate(p1, p2):
    if abs(p1 - p2) > 20:
        return True
    
    else:
        return False

def balanceTest():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    nickname_path = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

    with open(nickname_path) as nickname_file:
        nickname_data = json.load(nickname_file)

    nickname = nickname_data["name"]

    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    camDelay = False

    initialPositionSet = False
    balanceStarted = False
    leftbalanceStarted = False
    rightbalanceStarted = False
    balanceStartTime = 0

    prepStartTime = time.time()
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
            kneeHip = detector.findKneeHip(image)
            
            # handList_user = detector.findHand(image)
            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)

            if kneeHip is not None and len(kneeHip) >= 2:
                leftShoulder = [kneeHip[0][0], kneeHip[0][1]]
                rightShoulder = [kneeHip[1][0], kneeHip[1][1]]
                leftHip = [kneeHip[2][0], kneeHip[2][1]]
                rightHip = [kneeHip[3][0], kneeHip[3][1]]
                leftKnee = [kneeHip[4][0], kneeHip[4][1]]
                rightKnee = [kneeHip[5][0], kneeHip[5][1]]

                endTimer = time.time()

                # 초기 위치 설정
                if not initialPositionSet and time.time() - prepStartTime >= 6:
                    initialleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    initialrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])

                    initialPositionSet = True

                # 현재 허리와 무릎 사이의 간격 인식
                if initialPositionSet and not balanceStarted:
                    currentleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    currentrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])

                    # 왼쪽 무릎을 들었을 경우 시작
                    if currentleftKneeHipDistance < initialleftKneeHipDistance - 10:
                        initialleftkneePosition = leftKnee[0]
                        initialrightkneePosition = rightKnee[0]
                        initialleftshoulderPosition = leftShoulder[0]
                        initialrightshoulderPosition = rightShoulder[0]
                        balanceStartTime = time.time()
                        leftbalanceStarted = True
                        balanceStarted = True
                    # 오른쪽 무릎을 들었을 경우 시작
                    elif currentrightKneeHipDistance < initialrightKneeHipDistance - 10:
                        initialleftkneePosition = leftKnee[0]
                        initialrightkneePosition = rightKnee[0]
                        initialleftshoulderPosition = leftShoulder[0]
                        initialrightshoulderPosition = rightShoulder[0]
                        balanceStartTime = time.time()
                        rightbalanceStarted = True
                        balanceStarted = True
                # 왼 무릎으로 시작할 경우
                if leftbalanceStarted:
                    currentleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    # 60초가 지나거나, 무릎을 놓치거나, 어깨가 흔들리거나, 무릎이 흔들릴 경우 종료
                    if currentleftKneeHipDistance > initialleftKneeHipDistance - 3 or differenceCalculate(initialleftshoulderPosition, leftShoulder[0]) or differenceCalculate(initialrightshoulderPosition, rightShoulder[0]) or differenceCalculate(initialleftkneePosition, leftKnee[0]) or endTimer - startTimer >= 60:
                        ps.playsound(path + "jump.mp3")

                        balanceTime = round(time.time() - balanceStartTime, 3)

                        # rating = 0

                        # if balanceTime >= 20:
                        #     rating = 0

                        # else:
                        #     rating = 1

                        print("Balance Time:", balanceTime, "seconds")

                        value = [nickname, 0, 0, 0, 0, balanceTime, 0]

                        api.gamedata_api("/BasicData", "POST", value)
                        api.gamedata_api(f"/BasicData/{nickname}/update_rating", "PUT", value)

                        break

                elif rightbalanceStarted:
                    currentrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])
                    # 60초가 지나거나, 무릎을 놓치거나, 어깨가 흔들리거나, 무릎이 흔들릴 경우 종료
                    if currentrightKneeHipDistance > initialrightKneeHipDistance - 3 or differenceCalculate(initialleftshoulderPosition, leftShoulder[0]) or differenceCalculate(initialrightshoulderPosition, rightShoulder[0]) or differenceCalculate(initialrightkneePosition, rightKnee[0]) or endTimer - startTimer >= 60:
                        ps.playsound(path + "jump.mp3")

                        balanceTime = round(time.time() - balanceStartTime, 3)

                        # rating = 0

                        # if balanceTime >= 20:
                        #     rating = 0

                        # else:
                        #     rating = 1

                        print("Balance Time:", balanceTime, "seconds")

                        value = [nickname, 0, 0, 0, 0, balanceTime, 0]

                        api.gamedata_api("/BasicData", "POST", value)
                        api.gamedata_api(f"/BasicData/{nickname}/update_rating", "PUT", value)

                        break
            
        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')
        
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