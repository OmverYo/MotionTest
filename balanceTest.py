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
            results = detector.findKneeHip(image)
            # handList_user = detector.findHand(image)

            # value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

            # api.gamedata_api("/HandData/1", "PUT", value)

            if results is not None and len(results) >= 2:
                leftHip = [results[0][0], results[0][1]]
                leftKnee = [results[1][0], results[1][1]]

                endTimer = time.time()

                if not initialPositionSet and time.time() - prepStartTime >= 3:
                    initialKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    initialPositionSet = True

                if initialPositionSet and not balanceStarted:
                    currentKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    if currentKneeHipDistance < initialKneeHipDistance - 10:
                        balanceStartTime = time.time()
                        balanceStarted = True

                if balanceStarted:
                    currentKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                    if currentKneeHipDistance > initialKneeHipDistance - 3 or endTimer - startTimer >= 60:
                        balanceTime = round(time.time() - balanceStartTime, 3)

                        rating = 0

                        if balanceTime >= 20:
                            rating = 0

                        else:
                            rating = 1

                        print("Balance Time:", balanceTime, "seconds")

                        value = [0, 0, 0, 0, balanceTime, rating]

                        api.gamedata_api("/BasicData", "POST", value)

                        user_cam.release()

                        api.gamedata_api("/ProgramData", "POST", 0)

                        break
            
        except:
            success, image = user_cam.read()
        
        flipFrame = cv2.flip(image, 1)
        ret_val, buffer = cv2.imencode('.jpg', flipFrame)
        encodedImage = buffer.tobytes()
        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encodedImage + b'\r\n')

    api.gamedata_api("/ProgramData", "DELETE", None)

    user_cam.release()