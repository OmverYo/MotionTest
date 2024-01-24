import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def balanceTest():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
    
    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    camDelay = False
    # 초기 위치 설정 및 준비 시간 계산을 위한 변수
    initialPositionSet = False
    balanceStarted = False
    balanceStartTime = 0

    prepStartTime = time.time()
    startTimer = time.time()
    endTimer = time.time()

    while True:
        endTimer = time.time()
        if endTimer - startTimer >= 3 and camDelay is False:
            camDelay = True
            api.gamedata_api("/BackgroundData", "DELETE", None)
            api.gamedata_api("/ProgramData", "POST", 1)
        if endTimer - startTimer >= 6:
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
            shoulder = detector.findKneeHip(image)
            
            # handList_user = detector.findHand(image)
            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]
            # api.gamedata_api("/HandData/1", "PUT", value)

            if kneeHip is not None and len(kneeHip) >= 2:
                leftHip = [kneeHip[0][0], kneeHip[0][1]]
                rightHip = [kneeHip[1][0], kneeHip[1][1]]
                leftKnee = [kneeHip[2][0], kneeHip[2][1]]
                rightKnee = [kneeHip[3][0], kneeHip[3][1]]
                leftShoulder = [shoulder[0][0], shoulder[0][1]]
                rightShoulder = [shoulder[1][0], shoulder[1][1]]

                endTimer = time.time()

                if not initialPositionSet and time.time() - prepStartTime >= 6:
                    initialleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    initialrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])
                    initialleftshoulderPosition = leftShoulder
                    initialrightshoulderPosition = rightShoulder
                    initialPositionSet = True

                if initialPositionSet and not balanceStarted:
                    currentleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    currentrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])
                    if currentleftKneeHipDistance < initialleftKneeHipDistance - 10 or currentrightKneeHipDistance < initialrightKneeHipDistance - 10:
                        balanceStartTime = time.time()
                        balanceStarted = True

                if balanceStarted:
                    currentleftKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    currentrightKneeHipDistance = abs(rightKnee[1] - rightHip[1])
                    if currentleftKneeHipDistance > initialleftKneeHipDistance - 3 or currentrightKneeHipDistance > initialrightKneeHipDistance - 3 or  endTimer - startTimer >= 60:
                        ps.playsound(path + "jump.mp3")

                        balanceTime = round(time.time() - balanceStartTime, 3)

                        # rating = 0

                        # if balanceTime >= 20:
                        #     rating = 0

                        # else:
                        #     rating = 1

                        print("Balance Time:", balanceTime, "seconds")

                        value = [0, 0, 0, 0, balanceTime, 0]

                        api.gamedata_api("/BasicData", "POST", value)
                        api.gamedata_api("/BasicData/1/update_rating", "PUT", value)

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
            api.gamedata_api("/ProgramData", "POST", 0)

            user_cam.release()
            
            break
        
        ret_val, image = user_cam.read()
        flipFrame = cv2.flip(image, 1)
        ret, buffer = cv2.imencode('.jpg', flipFrame)
        frame = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    api.gamedata_api("/ProgramData", "DELETE", None)

    user_cam.release()