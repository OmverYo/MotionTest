import cv2, time
import poseModule as pm
import api
import playsound as ps
import pathlib

def balanceTest():
    path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"

    # 초기 위치 설정 및 준비 시간 계산을 위한 변수
    initialPositionSet = False
    balanceStarted = False
    balanceStartTime = 0

    print("정자세로 서서 준비하세요. 3초 후에 시작합니다.")
    prepStartTime = time.time()

    user_cam = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    api.gamedata_api("/ProgramData", "POST", 1)

    startTimer = int(time.time())
    endTimer = int(time.time())

    while user_cam.isOpened():
        success, image = user_cam.read()

        try:
            endTimer = int(time.time())
            try:
                image = detector.findPose(image)
                results = detector.findKneeHip(image)
                handList_user = detector.findHand(image)

                value = [handList_user[1][1], handList_user[1][2], handList_user[0][1], handList_user[0][2]]

                # api.gamedata_api("/HandData/1", "PUT", value)

                leftHip = [results[0][0], results[0][1]]
                leftKnee = [results[1][0], results[1][1]]

            except:
                pass

            if not initialPositionSet and time.time() - prepStartTime > 3:
                initialKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                initialPositionSet = True
                ps.playsound(path + "static/audio.mp3")

            if initialPositionSet and not balanceStarted:
                currentKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                if currentKneeHipDistance < initialKneeHipDistance - 10:  # 무릎과 허리 사이의 거리가 좁아졌을 때 (측정 시작 임계값. 이 값이 클수록 더 큰 움직임을 필요로 함)
                    balanceStartTime = time.time()
                    balanceStarted = True

            if balanceStarted:
                currentKneeHipDistance = abs(leftKnee[1] - leftHip[1])
                if currentKneeHipDistance > initialKneeHipDistance - 3 or endTimer - startTimer >= 60:  # 무릎과 허리 사이의 거리가 다시 늘어났을 때 (무너진 것으로 간주되는 임계값. 이 값이 클수록 더 민감하게 반응)
                    balanceTime = round(time.time() - balanceStartTime, 3)

                    rating = 0

                    if balanceTime >= 20:
                        rating = 0

                    else:
                        rating = 1

                    print("평형 유지 시간:", balanceTime, "초")

                    value = [0, 0, 0, 0, balanceTime, rating]

                    api.gamedata_api("/BasicData", "POST", value)

                    user_cam.release()

                    api.gamedata_api("/ProgramData", "POST", 0)

                    break
        
        except:
            success, image = user_cam.read()

        ret_val, buffer = cv2.imencode('.jpg', image)

        image = buffer.tobytes()

        yield (b'--image\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
    
    api.gamedata_api("/ProgramData", "DELETE", None)
    
    user_cam.release()